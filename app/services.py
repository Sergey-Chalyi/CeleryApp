"""Service layer for business logic and data operations."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import User, Address, CreditCard, get_db_session

class UserService:
    """Service class for user-related operations."""
    
    @staticmethod
    def get_user_by_external_id(external_id: int) -> Optional[User]:
        """Get user by external ID from JSONPlaceholder."""
        db = get_db_session()
        try:
            return db.query(User).filter(User.external_id == external_id).first()
        finally:
            db.close()
    
    @staticmethod
    def get_user_with_relations(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user with all related data (addresses and credit cards)."""
        db = get_db_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'external_id': user.external_id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'website': user.website,
                'company_name': user.company_name,
                'company_catchphrase': user.company_catchphrase,
                'company_bs': user.company_bs,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'addresses': [
                    {
                        'id': addr.id,
                        'street_number': addr.street_number,
                        'street_name': addr.street_name,
                        'city': addr.city,
                        'state': addr.state,
                        'country': addr.country,
                        'postal_code': addr.postal_code,
                        'created_at': addr.created_at.isoformat() if addr.created_at else None
                    } for addr in user.addresses
                ],
                'credit_cards': [
                    {
                        'id': card.id,
                        'card_number': card.card_number,
                        'card_type': card.card_type,
                        'expiry_date': card.expiry_date,
                        'created_at': card.created_at.isoformat() if card.created_at else None
                    } for card in user.credit_cards
                ]
            }
        finally:
            db.close()
    
    @staticmethod
    def get_all_users(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination."""
        db = get_db_session()
        try:
            users = db.query(User).offset(offset).limit(limit).all()
            return [
                {
                    'id': user.id,
                    'external_id': user.external_id,
                    'name': user.name,
                    'username': user.username,
                    'email': user.email,
                    'addresses_count': len(user.addresses),
                    'credit_cards_count': len(user.credit_cards)
                } for user in users
            ]
        finally:
            db.close()

class AddressService:
    """Service class for address-related operations."""
    
    @staticmethod
    def get_addresses_by_user_id(user_id: int) -> List[Dict[str, Any]]:
        """Get all addresses for a specific user."""
        db = get_db_session()
        try:
            addresses = db.query(Address).filter(Address.user_id == user_id).all()
            return [
                {
                    'id': addr.id,
                    'street_number': addr.street_number,
                    'street_name': addr.street_name,
                    'city': addr.city,
                    'state': addr.state,
                    'country': addr.country,
                    'postal_code': addr.postal_code,
                    'created_at': addr.created_at.isoformat() if addr.created_at else None
                } for addr in addresses
            ]
        finally:
            db.close()

class CreditCardService:
    """Service class for credit card-related operations."""
    
    @staticmethod
    def get_credit_cards_by_user_id(user_id: int) -> List[Dict[str, Any]]:
        """Get all credit cards for a specific user."""
        db = get_db_session()
        try:
            cards = db.query(CreditCard).filter(CreditCard.user_id == user_id).all()
            return [
                {
                    'id': card.id,
                    'card_number': card.card_number,
                    'card_type': card.card_type,
                    'expiry_date': card.expiry_date,
                    'created_at': card.created_at.isoformat() if card.created_at else None
                } for card in cards
            ]
        finally:
            db.close()

class StatsService:
    """Service class for statistics and analytics."""
    
    @staticmethod
    def get_comprehensive_stats() -> Dict[str, Any]:
        """Get comprehensive statistics about the application."""
        db = get_db_session()
        try:
            total_users = db.query(User).count()
            total_addresses = db.query(Address).count()
            total_credit_cards = db.query(CreditCard).count()
            
            # Users with addresses
            users_with_addresses = db.query(User).join(Address).distinct().count()
            
            # Users with credit cards
            users_with_credit_cards = db.query(User).join(CreditCard).distinct().count()
            
            # Users with both addresses and credit cards
            users_with_both = db.query(User).join(Address).join(CreditCard).distinct().count()
            
            return {
                'total_users': total_users,
                'total_addresses': total_addresses,
                'total_credit_cards': total_credit_cards,
                'users_with_addresses': users_with_addresses,
                'users_with_credit_cards': users_with_credit_cards,
                'users_with_both': users_with_both,
                'coverage_stats': {
                    'address_coverage_percent': round((users_with_addresses / total_users * 100), 2) if total_users > 0 else 0,
                    'credit_card_coverage_percent': round((users_with_credit_cards / total_users * 100), 2) if total_users > 0 else 0,
                    'full_coverage_percent': round((users_with_both / total_users * 100), 2) if total_users > 0 else 0
                }
            }
        finally:
            db.close()
