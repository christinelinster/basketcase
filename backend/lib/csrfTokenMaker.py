import secrets

def validate_csrf_token(request, token):

    stored_token = request.state.session.get("csrf_token")

    if not stored_token or not token:
        return False

    return secrets.compare_digest(
        token,
        stored_token
    )

def get_or_create_csrf_token(request):

    token = request.state.session.get("csrf_token")

    if not token:
        token = secrets.token_urlsafe(64)
        request.state.session["csrf_token"] = token

    return token
    