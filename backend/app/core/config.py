from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
RESTAURANTS_FILE = DATA_DIR / "restaurants.json"
