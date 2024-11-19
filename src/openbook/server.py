from fastapi import FastAPI

from openbook.endpoints import routers

app = FastAPI(title="BookClub")

for router in routers:
    app.include_router(router)
