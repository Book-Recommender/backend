from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from openbook.auth import session_secret_key
from openbook.endpoints import routers

app = FastAPI(title="BookClub")
app.add_middleware(SessionMiddleware, secret_key=session_secret_key, https_only=True)

for router in routers:
    app.include_router(router)
