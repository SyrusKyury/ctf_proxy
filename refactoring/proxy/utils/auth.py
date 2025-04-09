from ..constants import AUTHENTICATION_TOKEN
from fastapi import Request, HTTPException

def authenticate_request(request: Request):
    """
    Function to authenticate incoming requests.
    It checks the Authorization header against a predefined token.
    Raises HTTPException with status code 401 if the token does not match.
    """
    auth_header : str = request.headers.get("Authorization")
    if auth_header != AUTHENTICATION_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")