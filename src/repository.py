from abc import ABC, abstractmethod
from typing import Optional


class Repository(ABC):
    """저장소 추상 인터페이스 — 새 백엔드는 이 클래스를 구현하면 됨 (OCP)."""

    @abstractmethod
    def save(self, entity: dict) -> dict:
        """엔티티를 저장하고 저장된 객체를 반환한다."""

    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[dict]:
        """ID로 엔티티를 조회한다. 없으면 None."""

    @abstractmethod
    def find_all(self) -> list:
        """저장된 모든 엔티티를 반환한다."""

    @abstractmethod
    def update(self, entity_id: str, updates: dict) -> Optional[dict]:
        """ID에 해당하는 엔티티를 수정하고 반환한다. 없으면 None."""

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """ID에 해당하는 엔티티를 삭제한다. 성공 여부를 반환한다."""
