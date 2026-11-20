import json
from collections.abc import Callable
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.core.config import CARTS_FILE
from app.schemas.cart import Cart
from filelock import FileLock


class CartRepository:
    def __init__(self, path: Path = CARTS_FILE):
        self.path = path.resolve()
        self.lock = FileLock(str(self.path) + ".lock")

    def _load(self) -> dict:
        try:
            with self.path.open(encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def get(self, customer_id: str) -> Cart | None:
        with self.lock:
            record = self._load().get(customer_id)
        return Cart.model_validate(record) if record is not None else None

    def change(self, customer_id: str, update: Callable[[Cart | None], Cart]) -> Cart:
        with self.lock:
            records = self._load()
            record = records.get(customer_id)
            cart = update(Cart.model_validate(record) if record is not None else None)
            updated = cart.model_dump(mode="json", exclude_computed_fields=True)
            if updated != record:
                records[customer_id] = updated
                self._save(records)
            return cart

    def _save(self, records: dict) -> None:
        temporary = NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.path.parent, delete=False
        )
        temporary_path = Path(temporary.name)
        try:
            with temporary as file:
                json.dump(records, file, indent=4)
                file.write("\n")
            temporary_path.replace(self.path)
        finally:
            temporary_path.unlink(missing_ok=True)
