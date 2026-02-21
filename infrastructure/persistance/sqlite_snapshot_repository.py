import sqlite3

from application.interfaces.snapshot_repository import SnapshotRepository
from domain.entitles.snapshot import Snapshot


class SqliteSnapshotRepository(SnapshotRepository):
    """
    Сохраняет Snapshot в SQLite базу.
    """

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                monitor_id TEXT,
                value TEXT,
                created_at TEXT
            )
                          """
        )

    def save(self, snapshot: Snapshot):
        self.conn.execute(
            "INSERT INTO SNAPSHOTS values (?, ?, ?)",
            (snapshot.monitor_id, str(snapshot.value), snapshot.created_at.isoformat()),
        )
        self.conn.commit()
