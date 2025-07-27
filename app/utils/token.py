# app/utils/token.py

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "fallback-secret"
SECURITY_SALT = os.getenv("SECURITY_SALT") or "email-confirmation-salt"
RESET_SALT = os.getenv("RESET_SALT") or "password-reset-salt"


serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_confirmation_token(email: str) -> str:
    """Generates a secure token for email confirmation."""
    return serializer.dumps(email, salt=SECURITY_SALT)


def verify_token(token: str, max_age: int = 3600) -> str | None:
    """Verifies the token and returns the original email."""
    try:
        return serializer.loads(token, salt=SECURITY_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None

def generate_reset_token(email: str) -> str:
    """Generates a secure token for password reset."""
    return serializer.dumps(email, salt=RESET_SALT)

def verify_reset_token(token: str, max_age: int = 3600) -> str | None:
    """Verifies password reset token and returns the original email."""
    try:
        return serializer.loads(token, salt=RESET_SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None

