from typing import Dict
from application.interfaces.task import Task
from domain.entitles.monitor import Monitor
from infrastructure.persistance.sqlite_task_repository import SqliteTaskRepository
from application.use_cases.monitor_check import MonitorCheckUseCase
from domain.tasks.monitor_task import MonitorTask
from infrastructure.fetchers.http_fetcher import HttpFetcher
from infrastructure.persistance.sqlite_snapshot_repository import SqliteSnapshotRepository

class TaskManager:
    def __init__(self, db_path="tasks.db"):
        self._tasks: Dict[str, Task] = {}
        self.repo = SqliteTaskRepository(db_path)
        self.fetcher = HttpFetcher()
        self.snapshot_repo = SqliteSnapshotRepository("snapshot.db")

    def add(self, task: MonitorTask, value_type="numeric"):
        if task.task_id in self._tasks:
            raise ValueError("Task already exists")

        self._tasks[task.task_id] = task
        task.run()
        self.repo.save(task, value_type)

    def stop(self, task_id: str):
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        task.stop()
        self.repo.update_status(task_id, "stopped")

    def list(self):
        return list(self._tasks.values())

    def remove(self, task_id: str):
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")
        task.stop()
        del self._tasks[task_id]
        self.repo.update_status(task_id, "stopped")

    def load_all(self):
        """Восстанавливаем задачи из БД и запускаем те, которые были running"""
        rows = self.repo.load_all()
        for row in rows:
            monitor = Monitor(row["monitor_id"], row["url"], row["selector"])
            use_case = MonitorCheckUseCase(self.fetcher, self.snapshot_repo, value_type=row["value_type"])
            task = MonitorTask(
                task_id=row["task_id"],
                monitor=monitor,
                interval_sec=row["interval_sec"],
                duration_sec=row["duration_sec"],
                use_case=use_case,
                alert_threshold=row["alert_threshold"]
            )
            self._tasks[task.task_id] = task
            if row["status"] == "running":
                task.run()