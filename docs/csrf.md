# CSRF Protection Guide for TestLegion

This document outlines the standard pattern for protecting all POST forms in the TestLegion project using CSRF tokens.

---

## ✅ When to use CSRF protection

**Always include CSRF protection for any form that:**

- Uses `method="post"`
- Submits sensitive or authenticated data (e.g. login, signup, analysis, logout, profile updates)
- Is accessible by logged-in users

---

## 🛡️ Step-by-step for new POST forms

### 1. Generate CSRF token in GET route

```python
from app.utils.csrf import generate_csrf_token

@router.get("/some-form", response_class=HTMLResponse)
async def show_form(request: Request):
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    return templates.TemplateResponse("some_form.html", {
        "request": request,
        "csrf_token": csrf_token
    })

# 2. Include token in the HTML form

<form method="post" action="/some-form">
  <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
  <!-- other inputs -->
  <button type="submit">Submit</button>
</form>

# 3. Validate CSRF token in POST route

@router.post("/some-form")
async def submit_form(request: Request):
    form = await request.form()
    form_token = form.get("csrf_token")
    session_token = request.session.get("csrf_token")

    if not session_token or form_token != session_token:
        raise HTTPException(status_code=403, detail="Invalid CSRF token")

    # continue handling form...

    📌 Notes

    The CSRF token is randomly generated per session, not per form.

    We store it in the session and compare it during each POST request.

    Make sure the user has a valid session (request.session) – use middleware.


🔁 Already implemented in these routes    

    | Route           | Protected |
| --------------- | --------- |
| `/signup-form`  | ✅ Yes     |
| `/login-form`   | ✅ Yes     |
| `/reanalyse`    | ✅ Yes     |
| `/admin/logout` | ✅ Yes     |

Future reminder

Whenever you create a new form, copy this guide, and remember to:

    Generate the token in GET

    Include it in the HTML

    Validate it in POST