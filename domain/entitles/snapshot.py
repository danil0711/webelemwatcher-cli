from datetime import datetime


class Snapshot:
    """
    Фиксирует значение на момент времени.
    """

    def __init__(self, monitor_id, value: str, created_at: datetime):
        self.monitor_id = monitor_id
        self.value = value
        self.created_at = created_at

    def __repr__(self):
        return f"Snapshot(monitor_id='{self.monitor_id}', value='{self.value}', created_at='{self.created_at}')"
