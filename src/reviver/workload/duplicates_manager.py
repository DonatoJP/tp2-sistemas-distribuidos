from . import Task
from typing import Dict
from reviver.state_saver import Storable
from reviver.log import create_logger
logger = create_logger('basic-holder')

class DuplicatesManager(Storable):
    name = "duplicates_manager"

    def __init__(self, by_workload = {}) -> None:
        self.by_workload: Dict[str, list] = by_workload
        super().__init__(self.name)
    
    def __str__(self) -> str:
        return f'DuplicatesManager {self.by_workload}'

    def register_task(self, task: Task):
        if task.workload_id not in self.by_workload.keys():
            self.by_workload[task.workload_id] = []

        self.by_workload[task.workload_id].append(task.task_id)
        logger.debug(f"Registered task {task.task_id} for workload {task.workload_id}")


    def is_duplicate(self, task: Task):
        if task.workload_id not in self.by_workload.keys():
            return False
        
        if task.task_id in self.by_workload[task.workload_id]:
            logger.debug(f"Found Duplicate task {task.task_id} for workload {task.workload_id} of tasks {len(self.by_workload[task.workload_id])}")

        return task.task_id in self.by_workload[task.workload_id]

    def export_state(self):
        ret = {}
        ret["by_workload"] = self.by_workload
        return ret
    
    @classmethod
    def from_state(cls, state):
        by_workload = state["by_workload"]
        return cls(by_workload)
