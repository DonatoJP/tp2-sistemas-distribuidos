import json
from ..holder import AbstractHolder

class AvgSAHolder(AbstractHolder):
    name = 'avg_sa_holder'

    def export_state(self):
        ret = super().export_state()
        ret["by_workload"] = self.by_workload
        ret["column"] = self.column
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    # def __init__(self, column, total_count = 0, positive_sa_count = 0, **kwargs) -> None:
    def __init__(self, column, by_workload={}, **kwargs) -> None:
        # self.total_count = total_count
        # self.positive_sa_count = positive_sa_count
        self.column = column
        self.by_workload = by_workload
        super().__init__(**kwargs)
    
    def _count_new_result(self, data: dict, workload_id):
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = {'total_count': 0, 'positive_sa_count': 0}
        self.by_workload[workload_id]['total_count'] += 1
        if int(data[self.column]):
            self.by_workload[workload_id]['positive_sa_count'] += 1

    def exec_operation(self, data, workload_id) -> list:
        for d in data:
            data_dict = json.loads(d)
            self._count_new_result(data_dict, workload_id)
    
    def end(self, workload_id):
        if self.by_workload[workload_id]['total_count'] == 0:
            result = {"Result": "inf"}
            return [(json.dumps(result), self.get_affinity(result))]
        
        result = {"Result": self.by_workload[workload_id]['positive_sa_count'] / self.by_workload[workload_id]['total_count']}
        return [(json.dumps(result), self.get_affinity(result))]