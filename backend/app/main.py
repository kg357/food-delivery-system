from app.api.routes.health import router as health
from fastapi import FastAPI

app = FastAPI()

app.include_router(health)