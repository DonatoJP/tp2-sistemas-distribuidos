from . import Task
from typing import Dict

class DuplicatesManager:
    def __init__(self) -> None:
        self.by_workload: Dict[str, list] = {}

    def register_task(self, task: Task):
        if task.workload_id not in self.by_workload.keys():
            self.by_workload[task.workload_id] = []

        self.by_workload[task.workload_id].append(task.task_id)

    def is_duplicate(self, task: Task):
        if task.workload_id not in self.by_workload.keys():
            return False
        
        if task.task_id in self.by_workload[task.workload_id]:
            print('Found Duplicate!')

        return task.task_id in self.by_workload[task.workload_id]