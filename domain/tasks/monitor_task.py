import threading
import time
from application.interfaces.task import Task
from application.use_cases.monitor_check import MonitorCheckUseCase
from datetime import datetime, timedelta
from infrastructure.events.event_bus import EventBus

bus = EventBus()


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
        self._last_run: datetime = datetime.now() - timedelta(seconds=self.interval_sec)

    def run(self):
        """
        Запуск задачи в отдельном потоке.
        """
        if self._thread and self._thread.is_alive():
            return  # Защита от повторного запуска

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        started_at = time.time()

        while not self._stop_event.is_set():
            self._last_run = datetime.now()
            if self.duration_sec and (time.time() - started_at > self.duration_sec):
                bus.emit(f"[{self.task_id}] duration exceeded. stopping.")
                break
            try:

                snapshot = self.use_case.execute(self.monitor)
                if self.alert_threshold is not None:
                    try:
                        value = float(snapshot.value)
                        if value >= self.alert_threshold:
                            bus.emit(
                                f"[ALERT] {self.task_id}: "
                                f"value {value} >= {self.alert_threshold}"
                            )
                    except ValueError:
                        pass
            except Exception as e:
                bus.emit(f"[{self.task_id}] Error fetching {self.monitor.url}: {e}")

            if self._stop_event.wait(self.interval_sec):
                break

    def status(self) -> str:
        if self._thread and self._thread.is_alive():
            return "running"
        return "stopped"

    def stop(self):
        super().stop()

        if (
            self._thread
            and self._thread.is_alive()
            and threading.current_thread() is not self._thread
        ):
            self._thread.join(timeout=2)
