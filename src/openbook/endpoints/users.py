from typing import Annotated

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request

from openbook.auth import oauth, verify_user
from openbook.database import get_db
from openbook.exceptions import UnauthenticatedError
from openbook.models.orm import User

router = APIRouter(tags=["users"])


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    """User login entrypoint."""
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)  # pyright: ignore [reportOptionalMemberAccess]


@router.get("/auth")
async def auth(request: Request, db: Annotated[Session, Depends(get_db)]) -> RedirectResponse:
    """OAuth Redirect URL."""
    try:
        token = await oauth.google.authorize_access_token(request)  # pyright: ignore [reportOptionalMemberAccess]
    except OAuthError:
        raise UnauthenticatedError

    userinfo = token.get("userinfo")

    if not userinfo:
        raise ValueError

    user_dict = dict(userinfo)

    id = user_dict["sub"]
    name = user_dict["name"]
    email = user_dict["email"]

    with db.begin():
        user = db.scalar(select(User).filter(User.id == id))

        if user is None:
            user = User(id=id, name=name, email=email)
            db.add(user)

    request.session["id_token"] = token.get("id_token")
    return RedirectResponse(url="/home")


@router.get("/logout")
async def logout(request: Request, user: Annotated[User, Depends(verify_user)]) -> RedirectResponse:
    """Log out the current user."""
    request.session.pop("id_token")
    return RedirectResponse(url="/home")


@router.get("/userinfo")
async def userinfo(request: Request, user: Annotated[User, Depends(verify_user)]) -> dict:
    """Get info about the current user."""
    return {
        "userinfo": {
            "id": user.id,
            "name": user.name,
        }
    }
