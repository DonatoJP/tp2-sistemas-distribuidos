from utils.workload import Task

class CentinelsManager:
    def __init__(self, previous_step_components) -> None:
        self.previous_step_components = previous_step_components
        self.received_centinels = {}
        self._centinel = 'END'

    def is_centinel(self, task: Task):
        return task.centinel
    
    def count_centinel(self, task: Task):
        if task.workload_id not in self.received_centinels:
            self.received_centinels[task.workload_id] = 0

        self.received_centinels[task.workload_id] += 1
    
    def are_all_received(self, task: Task):
        return self.received_centinels[task.workload_id] == self.previous_step_components
    
    def build_centinel(self, task: Task) -> bytes:
        centinel_task = Task(task.workload_id, '', True) # TODO: Deberiamos enviar el mismo task_id para los centinelas?
        return centinel_task.serialize()
    
    @property
    def centinel(self):
        return self._centinel