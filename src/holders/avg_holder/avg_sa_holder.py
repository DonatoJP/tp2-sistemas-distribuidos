import json
from ..holder import AbstractHolder

class AvgSAHolder(AbstractHolder):
    def __init__(self, column, **kwargs) -> None:
        self.total_count = 0
        self.positive_sa_count = 0
        self.column = column
        super().__init__()
    
    def _count_new_result(self, data: dict):
        self.total_count += 1
        if int(data[self.column]):
            self.positive_sa_count += 1

    def exec_operation(self, data) -> list:
        data_dict = json.loads(data)
        self._count_new_result(data_dict)
    
    def end(self):
        return {"result": self.positive_sa_count / self.total_count}