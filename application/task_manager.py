from typing import Dict

from application.interfaces.task import Task



class TaskManager:
    """
    Управляет всеми активными задачами.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def add(self, task: Task):
        if task.task_id in self._tasks:
            raise ValueError("Task already exists")

        self._tasks[task.task_id] = task
        task.run()

    def stop(self, task_id: str):
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        task.stop()

    def list(self):
        return list(self._tasks.values())

    def remove(self, task_id: str):
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError("Task not found")

        task.stop()
        del self._tasks[task_id]