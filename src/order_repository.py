from typing import Optional

from src.json_repository import JsonRepository

VALID_STATUSES = frozenset({"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"})


class OrderJsonRepository(JsonRepository):
    def __init__(self, file_path: str):
        super().__init__(file_path, id_key="order_id")

    def _validate_status(self, data: dict) -> None:
        if "status" in data and data["status"] not in VALID_STATUSES:
            raise ValueError(
                f"유효하지 않은 주문 상태: '{data['status']}'. "
                f"허용 상태: {sorted(VALID_STATUSES)}"
            )

    def save(self, entity: dict) -> dict:
        self._validate_status(entity)
        return super().save(entity)

    def update(self, entity_id: str, updates: dict) -> Optional[dict]:
        self._validate_status(updates)
        return super().update(entity_id, updates)

    def find_by_status(self, status: str) -> list:
        return [order for order in self.find_all() if order.get("status") == status]
