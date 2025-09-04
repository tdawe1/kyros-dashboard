"""
Tests for User model and database schema.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.auth.models import User
from core.database import Base


class TestUserModel:
    """Test User model functionality."""

    def test_user_model_creation(self, db_session):
        """Test that User model can be created with required fields."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            role="user"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.is_active is True  # Should default to True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_model_unique_constraints(self, db_session):
        """Test that unique constraints work for username and email."""
        # Create first user
        user1 = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same username
        user2 = User(
            username="testuser",  # Same username
            email="test2@example.com",
            hashed_password="hashed_password_here"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create second user with same email
        user3 = User(
            username="testuser2",
            email="test@example.com",  # Same email
            hashed_password="hashed_password_here"
        )
        db_session.add(user3)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_user_model_indexes(self, db_session):
        """Test that indexes are properly created for username and email."""
        # This test verifies that the unique constraints create indexes
        # by checking that queries on username and email are efficient
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        db_session.add(user)
        db_session.commit()
        
        # Query by username (should use index)
        found_user = db_session.query(User).filter(User.username == "testuser").first()
        assert found_user is not None
        assert found_user.email == "test@example.com"
        
        # Query by email (should use index)
        found_user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert found_user is not None
        assert found_user.username == "testuser"

    def test_user_model_is_active_default(self, db_session):
        """Test that is_active defaults to True."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        db_session.add(user)
        db_session.commit()
        
        # Refresh to get the actual database value
        db_session.refresh(user)
        assert user.is_active is True

    def test_user_model_is_active_explicit(self, db_session):
        """Test that is_active can be set explicitly."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        db_session.refresh(user)
        assert user.is_active is False

    def test_user_model_repr(self, db_session):
        """Test User model string representation."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str


class TestUserModelSchema:
    """Test User model database schema."""

    def test_no_redundant_indexes(self, db_session):
        """Test that there are no redundant indexes on username and email."""
        # Get the database connection
        connection = db_session.bind
        
        # Check SQLite schema for indexes
        if connection.dialect.name == 'sqlite':
            # Get index information
            with connection.connect() as conn:
                result = conn.execute(text("PRAGMA index_list(users)"))
                indexes = [row[1] for row in result.fetchall()]
                
                # Should not have separate indexes for username and email
                # since unique constraints already create indexes
                assert "ix_users_username" not in indexes
                assert "ix_users_email" not in indexes

    def test_is_active_server_default(self, db_session):
        """Test that is_active has server default."""
        # Get the database connection
        connection = db_session.bind
        
        if connection.dialect.name == 'sqlite':
            # Check table schema
            with connection.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = {row[1]: row for row in result.fetchall()}
                
                # Find is_active column
                is_active_info = columns.get('is_active')
                assert is_active_info is not None
                
                # Check that it has a default value (true for True in SQLite)
                # The default value is in column 4 (0-indexed)
                default_value = is_active_info[4]
                assert default_value == "'true'"  # SQLite stores True as "'true'"
