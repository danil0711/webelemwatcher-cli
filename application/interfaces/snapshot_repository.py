from abc import ABC, abstractmethod

from domain.entitles.snapshot import Snapshot


class SnapshotRepository(ABC):
    """Абстракция для сохранения и получения Snapshot'ов"""

    @abstractmethod
    def save(self, snapshot: Snapshot) -> None:
        """Сохраняет snapson в хранилище"""
        
    @abstractmethod
    def get_last(self, monitor_id: str) -> Snapshot | None:
        """
        Возвращает последний snapshot для данного монитора
        или None, если раньше не было snapshot.
        """
        pass
