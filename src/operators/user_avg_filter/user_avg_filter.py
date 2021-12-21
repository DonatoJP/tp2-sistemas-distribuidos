import json
import re
from ..operator import AbstractOperator

class UserAvgFilter(AbstractOperator):
    def __init__(self, **kwargs) -> None:
        self.users_cache = []
        self.general_avg = None
        super().__init__(**kwargs)

    def _build_output(self, data):
        return {"OwnerUserId": data["OwnerUserId"], "TotalScore": data["TotalScore"]}

    def parse_user_avg_message(self, data: dict) -> list:
        if self.general_avg == None:
            self.users_cache.append(data)
            return []
        else:
            if self.general_avg > data["Avg"]:
                return []
            
            return [ self._build_output(data) ]
    
    def parse_general_avg_message(self, data: dict) -> list:
        self.general_avg = data["Avg"]
        result = [self._build_output(x) for x in self.users_cache if x["Avg"] >= self.general_avg]
        self.users_cache = []
        return result

    def exec_operation(self, data, workload_id) -> list:
        before_grouping = []
        for item in data:
            data_dict = json.loads(item)
            if data_dict["User_Avg"]:
                before_grouping.append( [(json.dumps(x), self.get_affinity(x)) for x in self.parse_user_avg_message(data_dict)] )
            else:
                before_grouping.append( [(json.dumps(x), self.get_affinity(x)) for x in self.parse_general_avg_message(data_dict)] )

        before_grouping = [tup for item in before_grouping for tup in item]
        return self._group_by_ak(before_grouping)    
