import threading
import time
from application.interfaces.task import Task
from application.use_cases.monitor_check import MonitorCheckUseCase


class MonitorTask(Task):
    """
    Задача периодического мониторинга.
    """

    def __init__(
        self,
        task_id: str,
        monitor,
        interval_sec: int,
        duration_sec: int,
        use_case: MonitorCheckUseCase,
        alert_threshold: float | None = None,
    ):
        super().__init__(
            task_id=task_id,
            monitor=monitor,
            interval_sec=interval_sec,
            duration_sec=duration_sec,
            alert_threshold=alert_threshold,
        )
        self.use_case = use_case
        self._thread = None

    def run(self):
        """
        Запуск задачи в отдельном потоке.
        """
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        started_at = time.time()

        while not self._stop:
            if self.duration_sec and (time.time() - started_at > self.duration_sec):
                print(f"[{self.task_id}] duration exceeded. stopping.")
                break

            snapshot = self.use_case.execute(self.monitor)
            if self.alert_threshold is not None:
                try:
                    value = float(snapshot.value)
                    if value >= self.alert_threshold:
                        print(
                            f"[ALERT] {self.task_id}: "
                            f"value {value} >= {self.alert_threshold}"
                        )
                except ValueError:
                    pass

            time.sleep(self.interval_sec)

        self._stop = True

    def status(self) -> str:
        return "stopped" if self._stop else "running"
