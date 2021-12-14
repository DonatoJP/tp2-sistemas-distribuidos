import json
from ..holder import AbstractHolder
from io import StringIO
class GeneralAvg(AbstractHolder):
    def __init__(self, **kwargs) -> None:
        self.total_score = 0
        self.total_count = 0
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
    
