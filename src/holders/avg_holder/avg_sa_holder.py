import json
from ..holder import AbstractHolder

class AvgSAHolder(AbstractHolder):
    def __init__(self) -> None:
        self.total_count = 0
        self.positive_sa_count = 0
        super().__init__()
    
    def _count_new_result(self, data: dict, column: str):
        self.total_count += 1
        if int(data[column]):
            self.positive_sa_count += 1

    def exec_operation(self, data, **kwargs) -> list:
        data_dict = json.loads(data)
        self._count_new_result(data_dict, **kwargs)
    
    def end(self):
        return {"result": self.positive_sa_count / self.total_count}