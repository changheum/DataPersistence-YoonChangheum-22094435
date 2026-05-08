import json
import os
from typing import Optional

from src.repository import Repository


class JsonRepository(Repository):
    def __init__(self, file_path: str, id_key: str = "sample_id"):
        self._file_path = file_path
        self._id_key = id_key

    def _load(self) -> list:
        if not os.path.exists(self._file_path):
            return []
        with open(self._file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _dump(self, data: list) -> None:
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, entity: dict) -> dict:
        data = self._load()
        data.append(entity)
        self._dump(data)
        return entity

    def find_by_id(self, id: str) -> Optional[dict]:
        for item in self._load():
            if item.get(self._id_key) == id:
                return item
        return None

    def find_all(self) -> list:
        return self._load()

    def update(self, id: str, updates: dict) -> Optional[dict]:
        data = self._load()
        for item in data:
            if item.get(self._id_key) == id:
                item.update(updates)
                self._dump(data)
                return item
        return None

    def delete(self, id: str) -> bool:
        data = self._load()
        new_data = [item for item in data if item.get(self._id_key) != id]
        if len(new_data) == len(data):
            return False
        self._dump(new_data)
        return True
