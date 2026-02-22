import cmd
import uuid
import shlex
from domain.tasks.monitor_task import MonitorTask
from domain.entitles.monitor import Monitor
from domain.services.monitor_identity import generate_monitor_id
from infrastructure.fetchers.http_fetcher import HttpFetcher
from infrastructure.persistance.sqlite_snapshot_repository import (
    SqliteSnapshotRepository,
)
from application.use_cases.monitor_check import MonitorCheckUseCase


class MonitorShell(cmd.Cmd):
    intro = "Monitor daemon started. Type help or ?."
    prompt = "(monitor) "

    def __init__(self, task_manager):
        super().__init__()
        self.manager = task_manager

    def do_add(self, arg):
        """
        add <url> <selector> <interval> <duration> <threshold>
        """

        try:
            parts = shlex.split(arg)
            if len(parts) != 5:
                print("Usage: add <url> <selector> <interval> <duration> <threshold>")
                return

            url, selector, interval, duration, threshold = parts
            interval = int(interval)
            duration = int(duration)
            threshold = float(threshold)

            monitor_id = generate_monitor_id(url, selector, "numeric")
            monitor = Monitor(monitor_id, url, selector)

            fetcher = HttpFetcher()
            repo = SqliteSnapshotRepository("snapshot.db")
            use_case = MonitorCheckUseCase(fetcher, repo, value_type="numeric")

            task_id = str(uuid.uuid4())[:8]

            task = MonitorTask(
                task_id=task_id,
                monitor=monitor,
                interval_sec=interval,
                duration_sec=duration,
                use_case=use_case,
                alert_threshold=threshold,
            )

            self.manager.add(task)
            print(f"Task {task_id} started")

        except Exception as e:
            print("Error:", e)

    def do_ps(self, arg):
        """
        Show all tasks
        """

        if not self.manager.list():
            print("No tasks are running currently.")
        for task in self.manager.list():
            print(
                f"{task.task_id} | {task.monitor.url} | "
                f"{task.status()} | interval={task.interval_sec}"
            )

    def do_stop(self, arg):
        """
        stop <task_id>
        """
        try:
            self.manager.stop(arg.strip())
            print("Stopped.")
        except Exception as e:
            print("Error:", e)

    def do_exit(self, arg):
        """
        Exit daemon
        """
        print("Stopping all tasks...")
        for task in self.manager.list():
            task.stop()
        return True
