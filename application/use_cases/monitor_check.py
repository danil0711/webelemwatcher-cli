from datetime import datetime, timezone
from application.use_cases.extractor import Extractor
from domain.entitles.snapshot import Snapshot
from infrastructure.events.event_bus import EventBus

bus = EventBus()


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

        # Получаем предыдущий snapshot
        last_snapshot = self.snapshot_repository.get_last(monitor.id)

        changed = False
        if last_snapshot is not None:
            old_value = self._cast(last_snapshot.value)
            new_value = self._cast(value)
            
            changed = old_value != new_value
            
        # Создаём Snapshot
        snapshot = Snapshot(
            monitor_id=monitor.id, value=value, created_at=datetime.now(timezone.utc)
        )

        self.snapshot_repository.save(snapshot)

        if changed:
            bus.emit("VALUE CHANGED")

        return snapshot
    
    def _cast(self, value):
        """
        Преобразует значение в нужный тип:
        - numeric: удаляем все кроме цифр и точки, конвертируем в float
        - text: просто str
        """
        if self.extractor.value_type == "numeric":
            import re
            # сначала str()
            value_str = str(value)
            cleaned = re.sub(r"[^\d.]", "", value_str)
            try:
                return float(cleaned)
            except ValueError:
                bus.emit(f"[{self.fetcher}] Не удалось конвертировать число: '{value}'")
                return 0.0
        return str(value)

    def __repr__(self):
        return f"MonitorCheckUseCase(fetcher='{self.fetcher}', snapshot_repository='{self.snapshot_repository}', extractor='{self.extractor}')"
