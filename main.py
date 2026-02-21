import argparse
from ast import parse
import uuid


from application.use_cases.monitor_check import MonitorCheckUseCase
from domain.entitles.monitor import Monitor
from infrastructure.fetchers.http_fetcher import HttpFetcher
from infrastructure.persistance.sqlite_snapshot_repository import SqliteSnapshotRepository


def main():
    parser = argparse.ArgumentParser(description="Monitor a value on a webpage.")
    parser.add_argument("--url", required=True, help="URL страницы")
    parser.add_argument("--selector", required=True, help="CSS селектор элемента")
    parser.add_argument(
        "--value-type",
        choices=["text", "numeric"],
        default="text",
        help="Тип значения для нормализации",
    )
    parser.add_argument('--db', default='snapshot.db', help='Путь к SQLite базе')
    args = parser.parse_args()
    
    monitor = Monitor(
        monitor_id=str(uuid.uuid4()),
        url=args.url,
        selector=args.selector
    )
    
    fetcher = HttpFetcher()
    repo = SqliteSnapshotRepository(args.db)
    use_case = MonitorCheckUseCase(fetcher, repo, value_type=args.value_type)
    
    snapshot = use_case.execute(monitor)
    print(snapshot)
    
    print(f"[{snapshot.created_at.isoformat()}] Captured value: {snapshot.value}")
    
if __name__ == "__main__":
    main()