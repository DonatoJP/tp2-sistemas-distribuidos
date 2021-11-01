import json
from ..holder import AbstractHolder
from io import StringIO

class UserAvgHolder(AbstractHolder):
    def __init__(self, **kwargs) -> None:
        self.user_counters = {}
        super().__init__(**kwargs)

    def _process_line_of_chunk(self, line_data):
        dict_data = json.loads(line_data)
        if dict_data["OwnerUserId"] not in self.user_counters.keys():
            self.user_counters[dict_data["OwnerUserId"]] = (0, 0)
        
        # Tuple like (Sum(Score), Count(*))
        to_sum = (int(dict_data["Score"]), 1)
        actual = self.user_counters[dict_data["OwnerUserId"]]
        self.user_counters[dict_data["OwnerUserId"]] = tuple([sum(x) for x in zip(actual, to_sum)])
    
    def exec_operation(self, data, **kwargs) -> list:
        io_string = StringIO(data)
        for line in io_string:
            self._process_line_of_chunk(line)

    def _build_output(self, user_id, total_score, total_count):
        output = {}
        output["OwnerUserId"] = user_id
        output["TotalScore"] = total_score
        output["Avg"] = total_score / total_count
        output["User_Avg"] = True
        return output


    def end(self):
        result = [self._build_output(x[0], x[1][0], x[1][1]) for x in self.user_counters.items()]
        return [ (json.dumps(x), self.get_affinity(x)) for x in result ]
    
