"""Application configuration settings."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Database configuration
    DATABASE_URL = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/celeryapp'
    )
    
    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # API endpoints
    JSONPLACEHOLDER_USERS_URL = 'https://jsonplaceholder.typicode.com/users'
    RANDOM_DATA_ADDRESS_URL = 'https://random-data-api.com/api/address/random_address'
    RANDOM_DATA_CREDIT_CARD_URL = 'https://random-data-api.com/api/business_credit_card/random_card'
    
    # Task settings
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Periodic task intervals (in seconds)
    FETCH_USERS_INTERVAL = 300  # 5 minutes
    FETCH_ADDRESSES_INTERVAL = 600  # 10 minutes
    FETCH_CREDIT_CARDS_INTERVAL = 900  # 15 minutes
