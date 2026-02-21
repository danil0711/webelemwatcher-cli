from datetime import datetime, timezone
from application.use_cases.extractor import Extractor
from domain.entitles.snapshot import Snapshot


class MonitorCheckUseCase:
    """Выполняет цикл мониторинга:
    fetch -> extract -> snapshot -> save
    """

    def __init__(self, fetcher, snapshot_repository, value_type: str = "text"):
        """
        fetcher: объект, который умеет получать HTML по URL
        snapshot_repository: объект, который умеет сохранять Snapshot
        value_type: тип значений для Extractor (`text' | `numeric')
        """

        self.fetcher = fetcher
        self.snapshot_repository = snapshot_repository
        self.extractor = Extractor(value_type=value_type)

    def execute(self, monitor):
        # Получаем HTML:
        html = self.fetcher.fetch(monitor.url)

        # Извлекаем значение
        value = self.extractor.extract(html, monitor.selector)
        


        # Создаём Snapshot
        snapshot = Snapshot(
            monitor_id=monitor.id, value=value, created_at=datetime.now(timezone.utc)
        )

        self.snapshot_repository.save(snapshot)

        return snapshot

    def __repr__(self):
        return f"MonitorCheckUseCase(fetcher='{self.fetcher}', snapshot_repository='{self.snapshot_repository}', extractor='{self.extractor}')"
