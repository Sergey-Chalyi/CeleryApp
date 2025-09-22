"""Tests for database models and operations."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.database import User, Address, CreditCard

class TestUserModel:
    """Test User model."""
    
    def test_create_user(self, test_db):
        """Test creating a user."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com",
            phone="123-456-7890",
            website="test.com",
            company_name="Test Company",
            company_catchphrase="Test Catchphrase",
            company_bs="Test BS"
        )
        test_db.add(user)
        test_db.commit()
        
        assert user.id is not None
        assert user.external_id == 1
        assert user.name == "Test User"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_user_unique_constraints(self, test_db):
        """Test user unique constraints."""
        # Create first user
        user1 = User(
            external_id=1,
            name="User 1",
            username="user1",
            email="user1@example.com"
        )
        test_db.add(user1)
        test_db.commit()
        
        # Try to create user with same external_id
        user2 = User(
            external_id=1,
            name="User 2",
            username="user2",
            email="user2@example.com"
        )
        test_db.add(user2)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_user_relationships(self, test_db):
        """Test user relationships with addresses and credit cards."""
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
        
        # Test relationships
        assert len(user.addresses) == 1
        assert len(user.credit_cards) == 1
        assert user.addresses[0].street_name == "Main St"
        assert user.credit_cards[0].card_number == "1234-5678-9012-3456"

class TestAddressModel:
    """Test Address model."""
    
    def test_create_address(self, test_db):
        """Test creating an address."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        address = Address(
            user_id=user.id,
            street_number="123",
            street_name="Main Street",
            city="New York",
            state="NY",
            country="United States",
            postal_code="10001"
        )
        test_db.add(address)
        test_db.commit()
        
        assert address.id is not None
        assert address.user_id == user.id
        assert address.street_name == "Main Street"
        assert address.city == "New York"
    
    def test_address_foreign_key_constraint(self, test_db):
        """Test address foreign key constraint."""
        address = Address(
            user_id=999,  # Non-existent user
            street_number="123",
            street_name="Main Street",
            city="New York"
        )
        test_db.add(address)
        
        with pytest.raises(IntegrityError):
            test_db.commit()

class TestCreditCardModel:
    """Test CreditCard model."""
    
    def test_create_credit_card(self, test_db):
        """Test creating a credit card."""
        user = User(
            external_id=1,
            name="Test User",
            username="testuser",
            email="test@example.com"
        )
        test_db.add(user)
        test_db.commit()
        
        credit_card = CreditCard(
            user_id=user.id,
            card_number="4532-1234-5678-9012",
            card_type="visa",
            expiry_date="12/25"
        )
        test_db.add(credit_card)
        test_db.commit()
        
        assert credit_card.id is not None
        assert credit_card.user_id == user.id
        assert credit_card.card_number == "4532-1234-5678-9012"
        assert credit_card.card_type == "visa"
    
    def test_credit_card_foreign_key_constraint(self, test_db):
        """Test credit card foreign key constraint."""
        credit_card = CreditCard(
            user_id=999,  # Non-existent user
            card_number="4532-1234-5678-9012",
            card_type="visa",
            expiry_date="12/25"
        )
        test_db.add(credit_card)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
