from app.api.routes.health import router as health
from app.api.routes.menu import router as menu_router
from app.api.routes.restaurants import router as restaurants
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app. add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health)
app.include_router(restaurants)
app.include_router(menu_router)