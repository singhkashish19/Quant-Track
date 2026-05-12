"""
Authentication Routes

API endpoints for user authentication and token management.

Endpoints:
    POST /api/auth/register - Register new user
    POST /api/auth/login - Login user
    POST /api/auth/refresh-token - Refresh access token
    GET /api/auth/verify - Verify token and get current user
    POST /api/auth/logout - Logout (optional, for token blacklist)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.schemas import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserResponse,
    TokenResponse,
    AuthResponse,
    MessageResponse,
)
from app.auth.service import AuthService
from app.auth.dependencies import get_current_user
from app.database.models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Register a new user account.
    
    - **email**: User email address (must be unique)
    - **name**: User full name
    - **password**: Password (minimum 8 characters)
    
    Returns user data and authentication tokens.
    """
    try:
        # Register user
        user = AuthService.register_user(user_data, db)
        
        # Generate tokens
        from app.auth.security import create_access_token, create_refresh_token
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        
        return AuthResponse(
            user=UserResponse.from_attributes(user),
            tokens=tokens,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Login user with email and password.
    
    Returns user data and authentication tokens.
    
    - **email**: User email
    - **password**: User password
    """
    try:
        user, tokens = AuthService.login_user(credentials, db)
        
        return AuthResponse(
            user=UserResponse.from_attributes(user),
            tokens=tokens,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        )


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Generate new access token using refresh token.
    
    - **refresh_token**: Refresh token from login response
    
    Returns new access token (refresh token remains valid).
    """
    try:
        tokens = AuthService.refresh_access_token(token_data.refresh_token, db)
        return tokens
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get(
    "/verify",
    response_model=UserResponse,
    summary="Verify token and get current user",
)
async def verify_token(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Verify JWT token and return current user information.
    
    Requires valid access token in Authorization header.
    
    Returns: Current user data
    """
    return UserResponse.from_attributes(current_user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side)",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """
    Logout endpoint (token invalidation).
    
    Note: In this implementation, tokens are stateless. This endpoint
    exists for API completeness. Client should discard tokens locally.
    For production, implement token blacklist with Redis.
    
    Returns: Success message
    """
    return MessageResponse(
        message=f"User {current_user.email} logged out successfully"
    )
