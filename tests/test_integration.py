"""Integration tests for the complete application flow."""
import pytest
from unittest.mock import patch, MagicMock
from app.tasks import fetch_users_task, fetch_addresses_task, fetch_credit_cards_task
from app.services import UserService, StatsService
from app.database import User, Address, CreditCard

class TestIntegrationFlow:
    """Test complete application flow."""
    
    def test_complete_data_flow(self, test_db, mock_requests):
        """Test complete data flow from users to addresses to credit cards."""
        # Mock API responses
        users_response = MagicMock()
        users_response.json.return_value = [
            {
                "id": 1,
                "name": "John Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "website": "johndoe.com",
                "company": {
                    "name": "Test Company",
                    "catchPhrase": "Test Catchphrase",
                    "bs": "Test BS"
                }
            }
        ]
        users_response.raise_for_status.return_value = None
        
        address_response = MagicMock()
        address_response.json.return_value = {
            "street_number": "123",
            "street_name": "Main Street",
            "city": "New York",
            "state": "NY",
            "country": "United States",
            "postal_code": "10001"
        }
        address_response.raise_for_status.return_value = None
        
        credit_card_response = MagicMock()
        credit_card_response.json.return_value = {
            "credit_card_number": "4532-1234-5678-9012",
            "credit_card_type": "visa",
            "credit_card_expiry_date": "12/25"
        }
        credit_card_response.raise_for_status.return_value = None
        
        # Configure mock to return different responses for different URLs
        def mock_get(url, **kwargs):
            if "jsonplaceholder" in url:
                return users_response
            elif "address" in url:
                return address_response
            elif "credit_card" in url:
                return credit_card_response
            return MagicMock()
        
        mock_requests.side_effect = mock_get
        
        # Step 1: Fetch users
        users_result = fetch_users_task()
        assert users_result['status'] == 'success'
        assert users_result['created'] == 1
        
        # Verify user was created
        user = UserService.get_user_by_external_id(1)
        assert user is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        
        # Step 2: Fetch addresses
        addresses_result = fetch_addresses_task()
        assert addresses_result['status'] == 'success'
        assert addresses_result['addresses_created'] == 1
        
        # Verify address was created
        user_with_relations = UserService.get_user_with_relations(user.id)
        assert len(user_with_relations['addresses']) == 1
        assert user_with_relations['addresses'][0]['street_name'] == "Main Street"
        assert user_with_relations['addresses'][0]['city'] == "New York"
        
        # Step 3: Fetch credit cards
        credit_cards_result = fetch_credit_cards_task()
        assert credit_cards_result['status'] == 'success'
        assert credit_cards_result['credit_cards_created'] == 1
        
        # Verify credit card was created
        user_with_relations = UserService.get_user_with_relations(user.id)
        assert len(user_with_relations['credit_cards']) == 1
        assert user_with_relations['credit_cards'][0]['card_number'] == "4532-1234-5678-9012"
        assert user_with_relations['credit_cards'][0]['card_type'] == "visa"
        
        # Step 4: Verify final stats
        stats = StatsService.get_comprehensive_stats()
        assert stats['total_users'] == 1
        assert stats['total_addresses'] == 1
        assert stats['total_credit_cards'] == 1
        assert stats['users_with_addresses'] == 1
        assert stats['users_with_credit_cards'] == 1
        assert stats['users_with_both'] == 1
        assert stats['coverage_stats']['full_coverage_percent'] == 100.0
    
    def test_error_handling_in_flow(self, test_db, mock_requests):
        """Test error handling during the data flow."""
        # Mock API to return error for users
        mock_requests.side_effect = Exception("API Error")
        
        # Users task should fail
        with pytest.raises(Exception):
            fetch_users_task()
        
        # No users should be created
        users = test_db.query(User).all()
        assert len(users) == 0
        
        # Address and credit card tasks should handle no users gracefully
        addresses_result = fetch_addresses_task()
        assert addresses_result['status'] == 'success'
        assert addresses_result['message'] == 'No users found'
        
        credit_cards_result = fetch_credit_cards_task()
        assert credit_cards_result['status'] == 'success'
        assert credit_cards_result['message'] == 'No users found'
    
    def test_partial_api_failures(self, test_db, mock_requests):
        """Test handling partial API failures."""
        # Mock successful users response
        users_response = MagicMock()
        users_response.json.return_value = [
            {
                "id": 1,
                "name": "John Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "website": "johndoe.com",
                "company": {"name": "Test Company", "catchPhrase": "Test", "bs": "Test"}
            }
        ]
        users_response.raise_for_status.return_value = None
        
        # Mock successful address response
        address_response = MagicMock()
        address_response.json.return_value = {
            "street_number": "123",
            "street_name": "Main Street",
            "city": "New York",
            "state": "NY",
            "country": "United States",
            "postal_code": "10001"
        }
        address_response.raise_for_status.return_value = None
        
        # Mock credit card API to fail
        credit_card_response = MagicMock()
        credit_card_response.side_effect = Exception("Credit Card API Error")
        
        def mock_get(url, **kwargs):
            if "jsonplaceholder" in url:
                return users_response
            elif "address" in url:
                return address_response
            elif "credit_card" in url:
                raise Exception("Credit Card API Error")
            return MagicMock()
        
        mock_requests.side_effect = mock_get
        
        # Users should be created successfully
        users_result = fetch_users_task()
        assert users_result['status'] == 'success'
        
        # Addresses should be created successfully
        addresses_result = fetch_addresses_task()
        assert addresses_result['status'] == 'success'
        
        # Credit cards should handle error gracefully
        credit_cards_result = fetch_credit_cards_task()
        assert credit_cards_result['status'] == 'success'
        assert credit_cards_result['credit_cards_created'] == 0
        
        # Verify partial data
        stats = StatsService.get_comprehensive_stats()
        assert stats['total_users'] == 1
        assert stats['total_addresses'] == 1
        assert stats['total_credit_cards'] == 0
        assert stats['users_with_addresses'] == 1
        assert stats['users_with_credit_cards'] == 0
