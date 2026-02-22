from application.task_manager import TaskManager
from interface.shell import MonitorShell


def main():
    task_manager = TaskManager(db_path="tasks.db")
    task_manager.load_all() 
    shell = MonitorShell(task_manager)
    shell.cmdloop()


if __name__ == "__main__":
    main()