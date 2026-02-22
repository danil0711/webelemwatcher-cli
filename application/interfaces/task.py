from abc import ABC, abstractmethod
from datetime import datetime
from domain.entitles.monitor import Monitor


class Task(ABC):
    """
    Базовый класс для всех задач планировщика.
    """
    

    def __init__(
        self,
        task_id: str,
        monitor: Monitor,
        interval_sec: int,
        duration_sec: int,
        alert_threshold: float = None,
    ):
        self.task_id = task_id
        self.monitor = monitor
        self.interval_sec = interval_sec
        self.duration_sec = duration_sec
        self.alert_threshold = alert_threshold
        self.created_at = datetime.now()
        self._stop = False

    @abstractmethod
    def run(self):
        "Метод, выполняющий задачу"
        pass
    
    
    
    
    def stop(self):
        self._stop = True

    def __repr__(self):
        return (
            f"Task(task_id='{self.task_id}', monitor={self.monitor}, "
            f"interval_sec={self.interval_sec}, duration_sec={self.duration_sec}, "
            f"alert_threshold={self.alert_threshold}, created_at={self.created_at.isoformat()})"
        )
