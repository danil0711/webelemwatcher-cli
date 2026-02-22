import sqlite3
from typing import List
from domain.tasks.monitor_task import MonitorTask

class SqliteTaskRepository:
    """
    Хранит все задачи MonitorTask в SQLite.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                monitor_id TEXT,
                url TEXT,
                selector TEXT,
                interval_sec INTEGER,
                duration_sec INTEGER,
                alert_threshold REAL,
                value_type TEXT,
                status TEXT
            )
            """
        )
        self.conn.commit()

    def save(self, task: MonitorTask, value_type: str):
        """Сохраняем новую задачу или обновляем, если уже есть"""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO tasks 
            (task_id, monitor_id, url, selector, interval_sec, duration_sec, alert_threshold, value_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.task_id,
                task.monitor.id,
                task.monitor.url,
                task.monitor.selector,
                task.interval_sec,
                task.duration_sec,
                task.alert_threshold,
                value_type,
                "running" if not task._stop else "stopped"
            ),
        )
        self.conn.commit()

    def update_status(self, task_id: str, status: str):
        self.conn.execute(
            "UPDATE tasks SET status=? WHERE task_id=?", (status, task_id)
        )
        self.conn.commit()

    def load_all(self) -> List[dict]:
        """Возвращает все задачи из БД как список словарей"""
        cursor = self.conn.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append(
                {
                    "task_id": row[0],
                    "monitor_id": row[1],
                    "url": row[2],
                    "selector": row[3],
                    "interval_sec": row[4],
                    "duration_sec": row[5],
                    "alert_threshold": row[6],
                    "value_type": row[7],
                    "status": row[8],
                }
            )
        return tasks