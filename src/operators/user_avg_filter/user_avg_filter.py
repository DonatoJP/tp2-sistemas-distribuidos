import json
from os import name
import re
from ..operator import AbstractOperator

class UserAvgFilter(AbstractOperator):
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, by_workload={}, **kwargs) -> None:
        # self.users_cache = []
        # self.general_avg = None
        self.by_workload = by_workload
        super().__init__(**kwargs)

    def _build_output(self, data):
        return {"OwnerUserId": data["OwnerUserId"], "TotalScore": data["TotalScore"]}

    def parse_user_avg_message(self, data: dict, workload_id) -> list:
        if self.by_workload[workload_id]['general_avg'] == None:
            self.by_workload[workload_id]['users_cache'].append(data)
            return []
        else:
            if self.by_workload[workload_id]['general_avg'] > data["Avg"]:
                return []
            
            return [ self._build_output(data) ]
    
    def parse_general_avg_message(self, data: dict, workload_id) -> list:
        self.by_workload[workload_id]['general_avg'] = data["Avg"]
        result = [self._build_output(x) for x in self.by_workload[workload_id]['users_cache'] if x["Avg"] >= self.by_workload[workload_id]['general_avg']]
        self.by_workload[workload_id]['users_cache'] = []
        return result

    def exec_operation(self, data, workload_id) -> list:
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = {"users_cache": {}, "general_avg": None}

        before_grouping = []
        for item in data:
            data_dict = json.loads(item)
            if data_dict["User_Avg"]:
                before_grouping.append( [(json.dumps(x), self.get_affinity(x)) for x in self.parse_user_avg_message(data_dict, workload_id)] )
            else:
                before_grouping.append( [(json.dumps(x), self.get_affinity(x)) for x in self.parse_general_avg_message(data_dict, workload_id)] )

        before_grouping = [tup for item in before_grouping for tup in item]
        return self._group_by_ak(before_grouping)

    @classmethod
    def should_save_state(cls):
        return True
    
    @classmethod
    def should_track_duplicates(cls):
        return True

    def export_state(self):
        ret = super().export_state()
        ret['by_workload'] = self.by_workload
        return ret
