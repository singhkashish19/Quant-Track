"""
Authentication Service

Business logic for user authentication, registration, and token management.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.models import User
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.auth.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.logger import logger


class AuthService:
    """
    Authentication service handling user registration, login, and token management.
    """
    
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            User: Created user object
            
        Raises:
            ValueError: If email already exists
        """
        logger.info("Registering new user: %s", user_data.email)
        try:
            # Check if user exists
            existing_user = db.query(User).filter(
                User.email == user_data.email
            ).first()
            
            if existing_user:
                logger.warning("Registration attempt with existing email: %s", user_data.email)
                raise ValueError(f"Email {user_data.email} already registered")
            
            # Hash password
            hashed_password = hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=hashed_password,
                is_active=True,
                subscription_tier="free",
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info("User created successfully: %s", user_data.email)
            return user
            
        except IntegrityError as e:
            db.rollback()
            logger.error("Registration failed for %s: %s", user_data.email, e)
            raise ValueError(f"Registration failed: {str(e)}")
    
    @staticmethod
    def login_user(credentials: UserLogin, db: Session) -> tuple[User, TokenResponse]:
        """
        Authenticate user and return tokens.
        
        Args:
            credentials: Login credentials
            db: Database session
            
        Returns:
            tuple: (User object, TokenResponse with access and refresh tokens)
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        
        return user, tokens
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Refresh token string
            db: Database session
            
        Returns:
            TokenResponse: New access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid refresh token used")
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise ValueError("User not found or disabled")
        
        # Create new access token
        new_access_token = create_access_token(subject=user_id)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Return same refresh token
            token_type="bearer",
        )
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> User:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            User: User object
            
        Raises:
            ValueError: If user not found
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        return user
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        """
        Get user by email.
        
        Args:
            email: User email
            db: Database session
            
        Returns:
            User: User object or None if not found
        """
        return db.query(User).filter(User.email == email).first()
