import json
from ..holder import AbstractHolder
from io import StringIO

class UserAvgHolder(AbstractHolder):
    name = 'user_avg'

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
        dict_data = json.loads(line_data)
        if dict_data["OwnerUserId"] not in self.by_workload[workload_id]['user_counters'].keys():
            self.by_workload[workload_id]['user_counters'][dict_data["OwnerUserId"]] = (0, 0)
        
        # Tuple like (Sum(Score), Count(*))
        to_sum = (int(dict_data["Score"]), 1)
        actual = self.by_workload[workload_id]['user_counters'][dict_data["OwnerUserId"]]
        self.by_workload[workload_id]['user_counters'][dict_data["OwnerUserId"]] = tuple([sum(x) for x in zip(actual, to_sum)])
    
    def exec_operation(self, data, workload_id) -> list:
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = {'user_counters': {}}

        io_string = StringIO(data)
        for line in io_string:
            self._process_line_of_chunk(line, workload_id)

    def _build_output(self, user_id, total_score, total_count):
        output = {}
        output["OwnerUserId"] = user_id
        output["TotalScore"] = total_score
        output["Avg"] = total_score / total_count
        output["User_Avg"] = True
        return output


    def end(self, workload_id):
        output = [self._build_output(x[0], x[1][0], x[1][1]) for x in self.by_workload[workload_id]['user_counters'].items()]
        before_grouping = [ (json.dumps(x), self.get_affinity(x)) for x in output ]
        return self._group_by_ak(before_grouping)
    
