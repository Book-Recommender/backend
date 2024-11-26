import datetime
import hashlib
import os
from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from authlib.jose import JWTClaims, jwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from openbook.constants import settings
from openbook.database import get_db
from openbook.exceptions import UnauthenticatedError
from openbook.models.orm import User

session_secret_key = hashlib.sha256(os.urandom(1024)).hexdigest()


oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url=settings.oauth_discovery_url,
    client_id=settings.oauth_client_id,
    client_secret=settings.oauth_client_secret,
    client_kwargs={"scope": "openid profile email"},
)


async def verify_token(id_token: str) -> JWTClaims:
    """Verify JWT."""
    jwks = await oauth.google.fetch_jwk_set()  # pyright: ignore [reportOptionalMemberAccess]
    try:
        decoded_jwt = jwt.decode(s=id_token, key=jwks)
    except Exception:
        raise UnauthenticatedError
    metadata = await oauth.google.load_server_metadata()  # pyright: ignore [reportOptionalMemberAccess]
    if decoded_jwt["iss"] != metadata["issuer"]:
        raise UnauthenticatedError
    if decoded_jwt["aud"] != settings.oauth_client_id:
        raise UnauthenticatedError
    exp = datetime.datetime.fromtimestamp(decoded_jwt["exp"], tz=datetime.UTC)
    if exp < datetime.datetime.now(tz=datetime.UTC):
        raise UnauthenticatedError
    return decoded_jwt


async def verify_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
    """
    Verify that a user is logged in.

    Returns:
        The User if valid

    Raises:
        UnauthenticatedError if unauthenticated.
    """
    id_token = request.session.get("id_token")
    if id_token is None:
        raise UnauthenticatedError
    decoded_jwt = await verify_token(id_token=id_token)
    user_id = decoded_jwt["sub"]

    user = db.scalar(select(User).filter(User.id == user_id))
    if user is None:
        raise UnauthenticatedError

    return user
