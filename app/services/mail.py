import httpx
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.utils.token import generate_confirmation_token

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
RESEND_BASE_URL = "https://api.resend.com/emails"

# Path to the email templates
templates_email = Jinja2Templates(directory="app/templates/emails")

async def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using the Resend API.
    """
    if not RESEND_API_KEY:
        raise ValueError("Missing RESEND_API_KEY in .env")

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "from": EMAIL_FROM or "onboarding@resend.dev",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(RESEND_BASE_URL, headers=headers, json=data)

    if response.status_code >= 400:
        raise Exception(f"Email sending failed: {response.status_code} - {response.text}")

    return response.json()

async def render_email(template_name: str, context: dict) -> str:
    """
    Renders an email template with the given context.
    """
    # We create a fake Request object for Jinja2 rendering
    request = Request(scope={"type": "http"})
    return templates_email.TemplateResponse(template_name, {"request": request, **context}).body.decode()




