from datetime import datetime
import sqlite3

from application.interfaces.snapshot_repository import SnapshotRepository
from domain.entitles import monitor
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
        
    def get_last(self, monitor_id: str) -> Snapshot | None:
        cursor = self.conn.execute(
            """
            SELECT monitor_id, value, created_at
            FROM snapshots
            WHERE monitor_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (monitor_id, )
        )
        
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return Snapshot(
            monitor_id=row[0],
            value=row[1],
            created_at=datetime.fromisoformat(row[2])
        )
        