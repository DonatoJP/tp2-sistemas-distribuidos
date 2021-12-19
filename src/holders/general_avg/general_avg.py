import json
from ..holder import AbstractHolder
from io import StringIO
class GeneralAvg(AbstractHolder):
    name = 'general_avg'

    def export_state(self):
        ret = super().export_state()
        ret["total_score"] = self.total_score
        ret["total_count"] = self.total_count
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, total_score = 0, total_count = 0, **kwargs) -> None:
        self.total_score = total_score
        self.total_count = total_count
        super().__init__(**kwargs)

    def _process_line_of_chunk(self, line_data):
        dict_data = json.loads(line_data)
        self.total_count += 1
        self.total_score += int(dict_data["Score"])

    def exec_operation(self, data, **kwargs) -> list:
        io_string = StringIO(data)
        for line in io_string:
            self._process_line_of_chunk(line)

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

        return [ ( [json.dumps(result)] , x) for x in self.get_affinity() ]
    
