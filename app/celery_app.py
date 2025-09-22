"""Celery application configuration."""
from celery import Celery
from app.config import Config

# Create Celery instance
celery_app = Celery(
    'celeryapp',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['app.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer=Config.CELERY_TASK_SERIALIZER,
    accept_content=Config.CELERY_ACCEPT_CONTENT,
    result_serializer=Config.CELERY_RESULT_SERIALIZER,
    timezone=Config.CELERY_TIMEZONE,
    enable_utc=Config.CELERY_ENABLE_UTC,
    beat_schedule={
        'fetch-users': {
            'task': 'app.tasks.fetch_users_task',
            'schedule': Config.FETCH_USERS_INTERVAL,
        },
        'fetch-addresses': {
            'task': 'app.tasks.fetch_addresses_task',
            'schedule': Config.FETCH_ADDRESSES_INTERVAL,
        },
        'fetch-credit-cards': {
            'task': 'app.tasks.fetch_credit_cards_task',
            'schedule': Config.FETCH_CREDIT_CARDS_INTERVAL,
        },
    }
)

if __name__ == '__main__':
    celery_app.start()
