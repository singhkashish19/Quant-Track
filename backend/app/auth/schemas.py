"""
Authentication Schemas (Pydantic models)

Request and response schemas for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ==================== REQUEST SCHEMAS ====================

class UserRegister(BaseModel):
    """User registration request schema"""
    
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "trader@example.com",
                "name": "John Trader",
                "password": "SecurePassword123!",
            }
        }


class UserLogin(BaseModel):
    """User login request schema"""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "trader@example.com",
                "password": "SecurePassword123!",
            }
        }


class TokenRefresh(BaseModel):
    """Token refresh request schema"""
    
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ==================== RESPONSE SCHEMAS ====================

class UserResponse(BaseModel):
    """User response schema (no sensitive data)"""
    
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    is_active: bool = Field(..., description="Account status")
    subscription_tier: str = Field(..., description="Subscription tier")
    
    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, obj):
        return cls.model_validate(obj)


class TokenResponse(BaseModel):
    """Token response schema"""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class AuthResponse(BaseModel):
    """Complete authentication response"""
    
    user: UserResponse = Field(..., description="User information")
    tokens: TokenResponse = Field(..., description="Access and refresh tokens")


class MessageResponse(BaseModel):
    """Generic message response"""
    
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response schema"""
    
    detail: str = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")


# ==================== TOKEN PAYLOAD SCHEMAS ====================

class TokenData(BaseModel):
    """Token payload data"""
    
    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at time")
    type: str = Field(..., description="Token type (access/refresh)")
