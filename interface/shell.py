import cmd
from datetime import timedelta, datetime
import os
import time
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
    intro = "Parser started. Type help or ?."
    prompt = "(wewatcher) "

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
        Show all tasks.

        Usage:
            ps
            ps --real-time
        Options:
            --real-time Shows time until until task is triggered
        """
        real_time = "--real-time" in arg.split()
        if real_time:
            self._watch_tasks()
        else:
            self._print_tasks()

    def do_stop(self, arg):
        """
        stop <task_id>
        """
        try:
            self.manager.stop(arg.strip())
            print("Stopped.")
        except Exception as e:
            print("Error:", e)

    def do_kill_all(self, arg):
        """
        Kill all running tasks immediately
        Usage: kill_all
        """
        try:
            self.manager.kill_all()
        except Exception as e:
            print("Error", e)

    def do_rm_all_tasks(self, arg):
        """
        Remove all tasks
        Usage: rm_all_tasks
        """
        try:
            self.manager.remove_all()
        except Exception as e:
            print("Error", e)

    def do_exit(self, arg):
        """
        Exit daemon
        """
        print("Stopping all tasks...")
        for task in self.manager.list():
            task.stop()
        return True

    def _print_tasks(self):
        """Печатает текущие задачи один раз."""
        tasks = self.manager.list()
        if not tasks:
            print("No tasks are running currently.")
            return

        print(f"{'TaskID':8} | {'URL':30} | {'Status':8} | {'Next Trigger'}")
        print("-" * 70)
        for task in tasks:
            remaining = max(
                0,
                (
                    task._last_run
                    + timedelta(seconds=task.interval_sec)
                    - datetime.now()
                ).total_seconds(),
            )
            print(
                f"{task.task_id:8} | {task.monitor.url[:30]:30} | "
                f"{task.status():8} | {int(remaining)}s"
            )

    def _watch_tasks(self):
        """Постоянно показывает задачи с обновлением экрана каждую секунду."""
        try:
            while True:
                os.system("clear")  # на Windows можно "cls"
                self._print_tasks()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopped real-time ps.")
