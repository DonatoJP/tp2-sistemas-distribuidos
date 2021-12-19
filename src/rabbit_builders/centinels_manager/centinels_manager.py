from reviver.workload import Task
from reviver.state_saver import Storable
class CentinelsManager(Storable):
    name = "centinels_manager"

    def __init__(self, previous_step_components, received_centinels = {}) -> None:
        self.previous_step_components = previous_step_components
        self.received_centinels = received_centinels
        self._centinel = 'END'
        super().__init__(self.name)
    
    def __str__(self) -> str:
        return f'CentinelsManager {self.previous_step_components} {self.received_centinels}'

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

    def export_state(self):
        ret = {}
        ret["previous_step_components"] = self.previous_step_components
        ret["received_centinels"] = self.received_centinels
        return ret
    
    @classmethod
    def from_state(cls, state):
        previous_step_components = state['previous_step_components']
        received_centinels = state['received_centinels']
        return cls(previous_step_components, received_centinels)