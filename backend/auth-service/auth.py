"""
Authentication utilities
Handles password hashing, user creation, and authentication
"""

from passlib.context import CryptContext
from typing import Optional
import uuid
from datetime import datetime

from models import UserInDB

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory storage for development (replace with database in production)
# This is temporary until we properly integrate with PostgreSQL
users_db: dict[str, UserInDB] = {}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """
    Get user by email
    TODO: Replace with database query
    """
    return users_db.get(email)


async def create_user(email: str, password: str, full_name: Optional[str] = None) -> UserInDB:
    """
    Create a new user
    TODO: Replace with database insert
    """
    user = UserInDB(
        id=uuid.uuid4(),
        email=email,
        password_hash=get_password_hash(password),
        full_name=full_name,
        role="user",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    users_db[email] = user
    return user


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user with email and password
    """
    user = await get_user_by_email(email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # Update last_login_at
    user.last_login_at = datetime.utcnow()

    return user


async def verify_token(token: str) -> Optional[UserInDB]:
    """
    Verify a JWT token and return the user
    This is a helper that combines token decoding and user lookup
    """
    from jwt_handler import decode_token

    payload = decode_token(token)
    if not payload:
        return None

    email = payload.get("sub")
    if not email:
        return None

    return await get_user_by_email(email)


# Initialize with default admin user for development
async def initialize_default_users():
    """
    Create default users for development
    """
    # Check if admin exists
    admin_email = "admin@mlplatform.local"
    if not await get_user_by_email(admin_email):
        await create_user(
            email=admin_email,
            password="admin123",  # Change in production!
            full_name="System Administrator"
        )
        users_db[admin_email].role = "admin"
        print(f"Created default admin user: {admin_email}")


# Call on module import
import asyncio
asyncio.create_task(initialize_default_users())
