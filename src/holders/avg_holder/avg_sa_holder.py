import json
from ..holder import AbstractHolder

class AvgSAHolder(AbstractHolder):
    def __init__(self, column, **kwargs) -> None:
        self.total_count = 0
        self.positive_sa_count = 0
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