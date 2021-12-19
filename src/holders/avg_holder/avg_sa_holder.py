import json
from ..holder import AbstractHolder

class AvgSAHolder(AbstractHolder):
    name = 'avg_sa_holder'

    def export_state(self):
        ret = super().export_state()
        ret["total_count"] = self.total_count
        ret["positive_sa_count"] = self.positive_sa_count
        ret["column"] = self.column
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, column, total_count = 0, positive_sa_count = 0, **kwargs) -> None:
        self.total_count = total_count
        self.positive_sa_count = positive_sa_count
        self.column = column
        super().__init__(**kwargs)
    
    def _count_new_result(self, data: dict):
        self.total_count += 1
        if int(data[self.column]):
            self.positive_sa_count += 1

    def exec_operation(self, data) -> list:
        for d in data:
            data_dict = json.loads(d)
            self._count_new_result(data_dict)
    
    def end(self):
        if self.total_count == 0:
            result = {"Result": "inf"}
            return [(json.dumps(result), self.get_affinity(result))]
        
        result = {"Result": self.positive_sa_count / self.total_count}
        return [(json.dumps(result), self.get_affinity(result))]