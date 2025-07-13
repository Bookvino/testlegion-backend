import secrets
from fastapi import Request, HTTPException, status

# Key used to store the CSRF token in the session
SESSION_KEY = "csrf_token"

def generate_csrf_token(request: Request) -> str:
    """
    Generate a new CSRF token, store it in the user's session,
    and return it for use in forms.
    """
    token = secrets.token_urlsafe(32)  # Secure random token
    request.session[SESSION_KEY] = token
    return token


def validate_csrf_token(request: Request, token_from_form: str) -> None:
    """
    Validate the CSRF token submitted from the form against the one stored in session.
    If invalid or missing, raise 403 Forbidden.
    """
    token_in_session = request.session.get(SESSION_KEY)

    if not token_from_form or not token_in_session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is missing."
        )

    if token_from_form != token_in_session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is invalid."
        )

    # Optionally rotate token here to prevent reuse
    del request.session[SESSION_KEY]
