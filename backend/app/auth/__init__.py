"""Authentication module"""

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.auth.service import AuthService
from app.auth.dependencies import (
    get_current_user,
    get_current_active_user,
)
from app.auth.schemas import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserResponse,
    TokenResponse,
    AuthResponse,
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    # Service
    "AuthService",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    # Schemas
    "UserRegister",
    "UserLogin",
    "TokenRefresh",
    "UserResponse",
    "TokenResponse",
    "AuthResponse",
]
