import json
from pathlib import Path
from app.core.config import RESTAURANTS_FILE

def load_restaurants(path: Path = RESTAURANTS_FILE) -> list[dict]:
    with path.open() as f:
        return json.load(f)
