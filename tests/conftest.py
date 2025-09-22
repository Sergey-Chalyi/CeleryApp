"""Pytest configuration and fixtures."""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from app.database import Base, get_db_session
from app.celery_app import celery_app
from app.config import Config

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests for API calls."""
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture(scope="function")
def celery_app_test():
    """Test Celery app configuration."""
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url='memory://',
        result_backend='cache+memory://'
    )
    return celery_app

@pytest.fixture
def sample_user_data():
    """Sample user data from JSONPlaceholder API."""
    return {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        "phone": "1-770-736-8031 x56442",
        "website": "hildegard.org",
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets"
        }
    }

@pytest.fixture
def sample_address_data():
    """Sample address data from Random Data API."""
    return {
        "street_number": "123",
        "street_name": "Main Street",
        "city": "New York",
        "state": "NY",
        "country": "United States",
        "postal_code": "10001"
    }

@pytest.fixture
def sample_credit_card_data():
    """Sample credit card data from Random Data API."""
    return {
        "credit_card_number": "4532-1234-5678-9012",
        "credit_card_type": "visa",
        "credit_card_expiry_date": "12/25"
    }

@pytest.fixture
def mock_jsonplaceholder_response(sample_user_data):
    """Mock JSONPlaceholder API response."""
    mock_response = MagicMock()
    mock_response.json.return_value = [sample_user_data]
    mock_response.raise_for_status.return_value = None
    return mock_response

@pytest.fixture
def mock_address_response(sample_address_data):
    """Mock Random Data API address response."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_address_data
    mock_response.raise_for_status.return_value = None
    return mock_response

@pytest.fixture
def mock_credit_card_response(sample_credit_card_data):
    """Mock Random Data API credit card response."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_credit_card_data
    mock_response.raise_for_status.return_value = None
    return mock_response
