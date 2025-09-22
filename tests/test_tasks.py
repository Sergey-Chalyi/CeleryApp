"""Tests for Celery tasks."""
import pytest
from unittest.mock import patch, MagicMock
from app.tasks import fetch_users_task, fetch_addresses_task, fetch_credit_cards_task, get_user_stats
from app.database import User, Address, CreditCard

class TestFetchUsersTask:
    """Test fetch_users_task."""
    
    def test_fetch_users_success(self, test_db, mock_requests, mock_jsonplaceholder_response, sample_user_data):
        """Test successful user fetching."""
        mock_requests.return_value = mock_jsonplaceholder_response
        
        result = fetch_users_task()
        
        assert result['status'] == 'success'
        assert result['created'] == 1
        assert result['updated'] == 0
        
        # Check user was created in database
        user = test_db.query(User).filter(User.external_id == 1).first()
        assert user is not None
        assert user.name == sample_user_data['name']
        assert user.email == sample_user_data['email']
    
    def test_fetch_users_update_existing(self, test_db, mock_requests, mock_jsonplaceholder_response, sample_user_data):
        """Test updating existing user."""
        # Create existing user
        existing_user = User(
            external_id=1,
            name="Old Name",
            username="olduser",
            email="old@example.com"
        )
        test_db.add(existing_user)
        test_db.commit()
        
        mock_requests.return_value = mock_jsonplaceholder_response
        
        result = fetch_users_task()
        
        assert result['status'] == 'success'
        assert result['created'] == 0
        assert result['updated'] == 1
        
        # Check user was updated
        updated_user = test_db.query(User).filter(User.external_id == 1).first()
        assert updated_user.name == sample_user_data['name']
        assert updated_user.email == sample_user_data['email']
    
    def test_fetch_users_api_error(self, mock_requests):
        """Test handling API errors."""
        mock_requests.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            fetch_users_task()
    
    def test_fetch_users_request_timeout(self, mock_requests):
        """Test handling request timeout."""
        import requests
        mock_requests.side_effect = requests.RequestException("Timeout")
        
        with pytest.raises(Exception):
            fetch_users_task()

class TestFetchAddressesTask:
    """Test fetch_addresses_task."""
    
    def test_fetch_addresses_success(self, test_db, mock_requests, mock_address_response, sample_address_data):
        """Test successful address fetching."""
        # Create a user first
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        mock_requests.return_value = mock_address_response
        
        result = fetch_addresses_task()
        
        assert result['status'] == 'success'
        assert result['addresses_created'] == 1
        
        # Check address was created
        address = test_db.query(Address).filter(Address.user_id == user.id).first()
        assert address is not None
        assert address.street_name == sample_address_data['street_name']
        assert address.city == sample_address_data['city']
    
    def test_fetch_addresses_no_users(self, test_db, mock_requests):
        """Test address fetching when no users exist."""
        result = fetch_addresses_task()
        
        assert result['status'] == 'success'
        assert result['message'] == 'No users found'
        assert result['addresses_created'] == 0
    
    def test_fetch_addresses_api_error(self, test_db, mock_requests):
        """Test handling API errors in address fetching."""
        # Create a user first
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        mock_requests.side_effect = Exception("API Error")
        
        result = fetch_addresses_task()
        
        # Should handle error gracefully
        assert result['status'] == 'success'
        assert result['addresses_created'] == 0

class TestFetchCreditCardsTask:
    """Test fetch_credit_cards_task."""
    
    def test_fetch_credit_cards_success(self, test_db, mock_requests, mock_credit_card_response, sample_credit_card_data):
        """Test successful credit card fetching."""
        # Create a user first
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        mock_requests.return_value = mock_credit_card_response
        
        result = fetch_credit_cards_task()
        
        assert result['status'] == 'success'
        assert result['credit_cards_created'] == 1
        
        # Check credit card was created
        credit_card = test_db.query(CreditCard).filter(CreditCard.user_id == user.id).first()
        assert credit_card is not None
        assert credit_card.card_number == sample_credit_card_data['credit_card_number']
        assert credit_card.card_type == sample_credit_card_data['credit_card_type']
    
    def test_fetch_credit_cards_no_users(self, test_db, mock_requests):
        """Test credit card fetching when no users exist."""
        result = fetch_credit_cards_task()
        
        assert result['status'] == 'success'
        assert result['message'] == 'No users found'
        assert result['credit_cards_created'] == 0

class TestGetUserStatsTask:
    """Test get_user_stats task."""
    
    def test_get_user_stats_empty(self, test_db):
        """Test getting stats when database is empty."""
        result = get_user_stats()
        
        assert result['total_users'] == 0
        assert result['total_addresses'] == 0
        assert result['total_credit_cards'] == 0
    
    def test_get_user_stats_with_data(self, test_db):
        """Test getting stats with data."""
        # Create user
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create address
        address = Address(
            user_id=user.id,
            street_number="123",
            street_name="Main St",
            city="Test City"
        )
        test_db.add(address)
        
        # Create credit card
        credit_card = CreditCard(
            user_id=user.id,
            card_number="1234-5678-9012-3456",
            card_type="visa",
            expiry_date="12/25"
        )
        test_db.add(credit_card)
        test_db.commit()
        
        result = get_user_stats()
        
        assert result['total_users'] == 1
        assert result['total_addresses'] == 1
        assert result['total_credit_cards'] == 1
