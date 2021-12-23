import json
from ..holder import AbstractHolder
from io import StringIO
class GeneralAvg(AbstractHolder):
    name = 'general_avg'

    def export_state(self):
        ret = super().export_state()
        ret["by_workload"] = self.by_workload
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, by_workload = {}, **kwargs) -> None:
        self.by_workload = by_workload
        super().__init__(**kwargs)

    def _process_line_of_chunk(self, line_data, workload_id):
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = {'total_score': 0, 'total_count': 0}

        dict_data = json.loads(line_data)

        self.by_workload[workload_id]['total_count'] += 1
        self.by_workload[workload_id]['total_score'] += int(dict_data["Score"])

    def exec_operation(self, data, workload_id) -> list:
        io_string = StringIO(data)
        for line in io_string:
            self._process_line_of_chunk(line, workload_id)

    def _build_output(self, workload_id):
        output = {}
        output["User_Avg"] = False
        output["Avg"] = self.by_workload[workload_id]['total_score'] / self.by_workload[workload_id]['total_count']
        return output

    def get_affinity(self):
        for i in range(0, self.affinity_divider):
            if (not self.perform_affinity):
                yield ''
            else:
                yield i

    def end(self, workload_id):
        result = self._build_output(workload_id)

        return [ ( [json.dumps(result)] , x) for x in self.get_affinity() ]
    
