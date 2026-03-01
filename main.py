from application.task_manager import TaskManager
from infrastructure.config.yaml_task_loader import YamlTaskLoader
from infrastructure.persistance.sqlite_snapshot_repository import SqliteSnapshotRepository
from interface.shell import MonitorShell

from infrastructure.fetchers.http_fetcher import HttpFetcher
from application.use_cases.monitor_check import MonitorCheckUseCase


def main():
    # --- infrastructure ---
    fetcher = HttpFetcher()
    snapshot_repo = SqliteSnapshotRepository("snapshot.db")

    # --- use case ---
    monitor_check_use_case = MonitorCheckUseCase(
        fetcher=fetcher,
        snapshot_repository=snapshot_repo
    )

    # --- task manager ---
    task_manager = TaskManager(db_path="tasks.db", use_case=monitor_check_use_case)
    task_manager.load_all()

    # --- yaml loader ---
    loader = YamlTaskLoader(use_case=monitor_check_use_case)

    # --- shell ---
    shell = MonitorShell(task_manager=task_manager, loader=loader)
    shell.cmdloop()


if __name__ == "__main__":
    main()