# app/services/email_service.py

from app.services.mail import send_email, render_email
from app.utils.token import generate_confirmation_token, generate_reset_token
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


async def send_welcome_email(email: str):
    """
    Sends a welcome email to the user after successful signup and confirmation.
    """
    html_content = await render_email(
        "welcome_email.html",
        {"user_email": email}
    )
    await send_email(
        to_email=email,
        subject="Welcome to TestLegion",
        html_content=html_content
    )


async def send_confirmation_email(email: str):
    """
    Sends an email with a confirmation link to verify user's email address.
    """
    token = generate_confirmation_token(email)
    confirm_url = f"{BASE_URL}/confirm-email?token={token}"

    html_content = await render_email(
        "email_confirmation.html",
        {"confirm_url": confirm_url, "user_email": email}
    )

    await send_email(
        to_email=email,
        subject="Confirm your email address",
        html_content=html_content
    )


async def send_password_reset_email(email: str):
    """
    Sends a password reset email with a token link.
    """
    
    token = generate_reset_token(email)
    reset_url = f"{BASE_URL}/reset-password?token={token}"

    html_content = await render_email(
        "password_reset.html",
        {"reset_url": reset_url, "user_email": email}
    )

    await send_email(
        to_email=email,
        subject="Reset your password",
        html_content=html_content
    )
