import json
from ..holder import AbstractHolder

class GeneralAvg(AbstractHolder):
    def __init__(self, **kwargs) -> None:
        self.total_score = 0
        self.total_count = 0
        super().__init__(**kwargs)
    
    def exec_operation(self, data, **kwargs) -> list:
        dict_data = json.loads(data)
        self.total_count += 1
        self.total_score += dict_data["Score"]

    def _build_output(self):
        output = {}
        output["User_Avg"] = False
        output["Avg"] = self.total_score / self.total_count
        return output

    def get_affinity(self):
        for i in range(0, self.affinity_divider):
            if (not self.perform_affinity):
                yield ''
            else:
                yield i

    def end(self):
        result = self._build_output()

        return [ (json.dumps(result), x) for x in self.get_affinity() ]
    
