from app.api.routes.health import router as health
from app.api.routes.restaurants import router as restaurants
from fastapi import FastAPI

app = FastAPI()

app.include_router(health)
app.include_router(restaurants)
