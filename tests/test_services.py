"""Tests for service layer."""
import pytest
from app.services import UserService, AddressService, CreditCardService, StatsService
from app.database import User, Address, CreditCard

class TestUserService:
    """Test UserService."""
    
    def test_get_user_by_external_id(self, test_db):
        """Test getting user by external ID."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        found_user = UserService.get_user_by_external_id(1)
        assert found_user is not None
        assert found_user.external_id == 1
        assert found_user.name == "Test User"
    
    def test_get_user_by_external_id_not_found(self, test_db):
        """Test getting user by external ID when not found."""
        found_user = UserService.get_user_by_external_id(999)
        assert found_user is None
    
    def test_get_user_with_relations(self, test_db):
        """Test getting user with all relations."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        # Add address
        address = Address(
            user_id=user.id,
            street_number="123",
            street_name="Main St",
            city="Test City",
            state="TS",
            country="Test Country",
            postal_code="12345"
        )
        test_db.add(address)
        
        # Add credit card
        credit_card = CreditCard(
            user_id=user.id,
            card_number="1234-5678-9012-3456",
            card_type="visa",
            expiry_date="12/25"
        )
        test_db.add(credit_card)
        test_db.commit()
        
        user_data = UserService.get_user_with_relations(user.id)
        
        assert user_data is not None
        assert user_data['name'] == "Test User"
        assert len(user_data['addresses']) == 1
        assert len(user_data['credit_cards']) == 1
        assert user_data['addresses'][0]['street_name'] == "Main St"
        assert user_data['credit_cards'][0]['card_number'] == "1234-5678-9012-3456"
    
    def test_get_user_with_relations_not_found(self, test_db):
        """Test getting user with relations when user not found."""
        user_data = UserService.get_user_with_relations(999)
        assert user_data is None
    
    def test_get_all_users(self, test_db):
        """Test getting all users with pagination."""
        # Create multiple users
        for i in range(5):
            user = User(
                external_id=i + 1,
                name=f"User {i + 1}",
                username=f"user{i + 1}",
                email=f"user{i + 1}@example.com"
            )
            test_db.add(user)
        test_db.commit()
        
        users = UserService.get_all_users(limit=3, offset=0)
        assert len(users) == 3
        assert users[0]['name'] == "User 1"
        assert users[2]['name'] == "User 3"
        
        users_page2 = UserService.get_all_users(limit=3, offset=3)
        assert len(users_page2) == 2
        assert users_page2[0]['name'] == "User 4"

class TestAddressService:
    """Test AddressService."""
    
    def test_get_addresses_by_user_id(self, test_db):
        """Test getting addresses by user ID."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        # Add multiple addresses
        for i in range(3):
            address = Address(
                user_id=user.id,
                street_number=str(100 + i),
                street_name=f"Street {i + 1}",
                city=f"City {i + 1}",
                state="TS",
                country="Test Country",
                postal_code=f"1234{i}"
            )
            test_db.add(address)
        test_db.commit()
        
        addresses = AddressService.get_addresses_by_user_id(user.id)
        assert len(addresses) == 3
        assert addresses[0]['street_name'] == "Street 1"
        assert addresses[1]['street_name'] == "Street 2"
        assert addresses[2]['street_name'] == "Street 3"
    
    def test_get_addresses_by_user_id_empty(self, test_db):
        """Test getting addresses when user has none."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        addresses = AddressService.get_addresses_by_user_id(user.id)
        assert len(addresses) == 0

class TestCreditCardService:
    """Test CreditCardService."""
    
    def test_get_credit_cards_by_user_id(self, test_db):
        """Test getting credit cards by user ID."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        # Add multiple credit cards
        for i in range(2):
            credit_card = CreditCard(
                user_id=user.id,
                card_number=f"1234-5678-9012-345{i}",
                card_type="visa",
                expiry_date=f"12/2{i}"
            )
            test_db.add(credit_card)
        test_db.commit()
        
        credit_cards = CreditCardService.get_credit_cards_by_user_id(user.id)
        assert len(credit_cards) == 2
        assert credit_cards[0]['card_number'] == "1234-5678-9012-3450"
        assert credit_cards[1]['card_number'] == "1234-5678-9012-3451"

class TestStatsService:
    """Test StatsService."""
    
    def test_get_comprehensive_stats_empty(self, test_db):
        """Test getting stats when database is empty."""
        stats = StatsService.get_comprehensive_stats()
        
        assert stats['total_users'] == 0
        assert stats['total_addresses'] == 0
        assert stats['total_credit_cards'] == 0
        assert stats['users_with_addresses'] == 0
        assert stats['users_with_credit_cards'] == 0
        assert stats['users_with_both'] == 0
        assert stats['coverage_stats']['address_coverage_percent'] == 0
        assert stats['coverage_stats']['credit_card_coverage_percent'] == 0
        assert stats['coverage_stats']['full_coverage_percent'] == 0
    
    def test_get_comprehensive_stats_with_data(self, test_db):
        """Test getting stats with data."""
        # Create users
        user1 = User(
            external_id=1,
            name="User 1",
            username="user1",
            email="user1@example.com"
        )
        user2 = User(
            external_id=2,
            name="User 2",
            username="user2",
            email="user2@example.com"
        )
        test_db.add_all([user1, user2])
        test_db.commit()
        
        # Add address for user1
        address = Address(
            user_id=user1.id,
            street_number="123",
            street_name="Main St",
            city="Test City"
        )
        test_db.add(address)
        
        # Add credit card for user1
        credit_card = CreditCard(
            user_id=user1.id,
            card_number="1234-5678-9012-3456",
            card_type="visa",
            expiry_date="12/25"
        )
        test_db.add(credit_card)
        test_db.commit()
        
        stats = StatsService.get_comprehensive_stats()
        
        assert stats['total_users'] == 2
        assert stats['total_addresses'] == 1
        assert stats['total_credit_cards'] == 1
        assert stats['users_with_addresses'] == 1
        assert stats['users_with_credit_cards'] == 1
        assert stats['users_with_both'] == 1
        assert stats['coverage_stats']['address_coverage_percent'] == 50.0
        assert stats['coverage_stats']['credit_card_coverage_percent'] == 50.0
        assert stats['coverage_stats']['full_coverage_percent'] == 50.0
