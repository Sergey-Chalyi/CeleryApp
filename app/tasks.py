"""Celery tasks for data fetching and processing."""
import requests
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.celery_app import celery_app
from app.database import SessionLocal, User, Address, CreditCard
from app.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_session() -> Session:
    """Get database session for tasks."""
    return SessionLocal()

@celery_app.task(bind=True, max_retries=3)
def fetch_users_task(self):
    """Fetch users from JSONPlaceholder API and store in database."""
    try:
        logger.info("Starting fetch_users_task")
        
        # Fetch users from API
        response = requests.get(Config.JSONPLACEHOLDER_USERS_URL, timeout=30)
        response.raise_for_status()
        users_data = response.json()
        
        db = get_db_session()
        try:
            created_count = 0
            updated_count = 0
            
            for user_data in users_data:
                try:
                    # Check if user already exists
                    existing_user = db.query(User).filter(
                        User.external_id == user_data['id']
                    ).first()
                    
                    if existing_user:
                        # Update existing user
                        existing_user.name = user_data['name']
                        existing_user.username = user_data['username']
                        existing_user.email = user_data['email']
                        existing_user.phone = user_data.get('phone', '')
                        existing_user.website = user_data.get('website', '')
                        existing_user.company_name = user_data.get('company', {}).get('name', '')
                        existing_user.company_catchphrase = user_data.get('company', {}).get('catchPhrase', '')
                        existing_user.company_bs = user_data.get('company', {}).get('bs', '')
                        updated_count += 1
                    else:
                        # Create new user
                        new_user = User(
                            external_id=user_data['id'],
                            name=user_data['name'],
                            username=user_data['username'],
                            email=user_data['email'],
                            phone=user_data.get('phone', ''),
                            website=user_data.get('website', ''),
                            company_name=user_data.get('company', {}).get('name', ''),
                            company_catchphrase=user_data.get('company', {}).get('catchPhrase', ''),
                            company_bs=user_data.get('company', {}).get('bs', '')
                        )
                        db.add(new_user)
                        created_count += 1
                    
                    db.commit()
                    
                except IntegrityError as e:
                    logger.warning(f"Integrity error for user {user_data.get('id')}: {e}")
                    db.rollback()
                    continue
                except Exception as e:
                    logger.error(f"Error processing user {user_data.get('id')}: {e}")
                    db.rollback()
                    continue
            
            logger.info(f"fetch_users_task completed: {created_count} created, {updated_count} updated")
            return {
                'status': 'success',
                'created': created_count,
                'updated': updated_count,
                'total_processed': len(users_data)
            }
            
        finally:
            db.close()
            
    except requests.RequestException as e:
        logger.error(f"Request error in fetch_users_task: {e}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Unexpected error in fetch_users_task: {e}")
        raise self.retry(countdown=60, exc=e)

@celery_app.task(bind=True, max_retries=3)
def fetch_addresses_task(self):
    """Fetch address data for users and store in database."""
    try:
        logger.info("Starting fetch_addresses_task")
        
        db = get_db_session()
        try:
            # Get all users
            users = db.query(User).all()
            if not users:
                logger.warning("No users found for address fetching")
                return {'status': 'success', 'message': 'No users found'}
            
            created_count = 0
            
            for user in users:
                try:
                    # Fetch random address data
                    response = requests.get(Config.RANDOM_DATA_ADDRESS_URL, timeout=30)
                    response.raise_for_status()
                    address_data = response.json()
                    
                    # Create new address
                    new_address = Address(
                        user_id=user.id,
                        street_number=address_data.get('street_number', ''),
                        street_name=address_data.get('street_name', ''),
                        city=address_data.get('city', ''),
                        state=address_data.get('state', ''),
                        country=address_data.get('country', ''),
                        postal_code=address_data.get('postal_code', '')
                    )
                    db.add(new_address)
                    created_count += 1
                    
                except requests.RequestException as e:
                    logger.warning(f"Request error for user {user.id}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing address for user {user.id}: {e}")
                    continue
            
            db.commit()
            logger.info(f"fetch_addresses_task completed: {created_count} addresses created")
            return {
                'status': 'success',
                'addresses_created': created_count,
                'users_processed': len(users)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Unexpected error in fetch_addresses_task: {e}")
        raise self.retry(countdown=60, exc=e)

@celery_app.task(bind=True, max_retries=3)
def fetch_credit_cards_task(self):
    """Fetch credit card data for users and store in database."""
    try:
        logger.info("Starting fetch_credit_cards_task")
        
        db = get_db_session()
        try:
            # Get all users
            users = db.query(User).all()
            if not users:
                logger.warning("No users found for credit card fetching")
                return {'status': 'success', 'message': 'No users found'}
            
            created_count = 0
            
            for user in users:
                try:
                    # Fetch random credit card data
                    response = requests.get(Config.RANDOM_DATA_CREDIT_CARD_URL, timeout=30)
                    response.raise_for_status()
                    card_data = response.json()
                    
                    # Create new credit card
                    new_card = CreditCard(
                        user_id=user.id,
                        card_number=card_data.get('credit_card_number', ''),
                        card_type=card_data.get('credit_card_type', ''),
                        expiry_date=card_data.get('credit_card_expiry_date', '')
                    )
                    db.add(new_card)
                    created_count += 1
                    
                except requests.RequestException as e:
                    logger.warning(f"Request error for user {user.id}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing credit card for user {user.id}: {e}")
                    continue
            
            db.commit()
            logger.info(f"fetch_credit_cards_task completed: {created_count} credit cards created")
            return {
                'status': 'success',
                'credit_cards_created': created_count,
                'users_processed': len(users)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Unexpected error in fetch_credit_cards_task: {e}")
        raise self.retry(countdown=60, exc=e)

@celery_app.task
def get_user_stats():
    """Get statistics about users and their data."""
    db = get_db_session()
    try:
        total_users = db.query(User).count()
        total_addresses = db.query(Address).count()
        total_credit_cards = db.query(CreditCard).count()
        
        return {
            'total_users': total_users,
            'total_addresses': total_addresses,
            'total_credit_cards': total_credit_cards
        }
    finally:
        db.close()
