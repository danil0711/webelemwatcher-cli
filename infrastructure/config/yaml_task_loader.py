import yaml
from domain.services.monitor_identity import generate_monitor_id
from domain.tasks.monitor_task import MonitorTask
from domain.entitles.monitor import Monitor
from application.use_cases.monitor_check import MonitorCheckUseCase

class YamlTaskLoader:
    """
    Загружает задачи MonitorTask из YAML-файла.
    """

    def __init__(self, use_case: MonitorCheckUseCase):
        self.use_case = use_case

    def load_tasks(self, path: str) -> list[MonitorTask]:
        if not path:
            print("⚠️ path argument is not provided in load_tasks.")
            return []
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        tasks = []
        for task_cfg in config.get("tasks", []):
            monitor_cfg = task_cfg.get("monitor")
            if not monitor_cfg:
                print(f"⚠ Task {task_cfg.get('id')} missing monitor section. Skipped.")
                continue

            monitor_id = generate_monitor_id(
                monitor_cfg["url"],
                monitor_cfg["selector"],
                "numeric"
            )

            monitor = Monitor(
                monitor_id=monitor_id,
                url=monitor_cfg["url"],
                selector=monitor_cfg["selector"]
            )

            task = MonitorTask(
                task_id=task_cfg["id"], 
                monitor=monitor,
                interval_sec=task_cfg["interval_sec"],
                duration_sec=task_cfg["duration_sec"],
                use_case=self.use_case,
                alert_threshold=task_cfg.get("alert_threshold")
            )
            tasks.append(task)
        return tasks
    
    
# Tasks YAML example 
# tasks:
#   - id: "task1"
#     monitor:
#       url: "https://www.worldometers.info"
#       selector: "div.rts-counter"
#     interval_sec: 10
#     duration_sec: 300
#     alert_threshold: 10000000