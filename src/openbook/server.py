from fastapi import FastAPI

from openbook.endpoints import routers

app = FastAPI(title="BookClub")

for router in routers:
    app.include_router(router)


@app.get("/")
async def index() -> str:
    """Index function."""
    return "hello"
