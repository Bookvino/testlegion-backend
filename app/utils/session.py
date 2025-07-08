from fastapi import Request, HTTPException, status
from starlette.responses import RedirectResponse

def require_login(request: Request):
    if "user_id" not in request.session:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return request

