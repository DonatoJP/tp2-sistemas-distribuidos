import json, datetime
from ..operator import AbstractOperator

class Intersector(AbstractOperator):
    name = 'intersector-operator'

    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, by_workload={}, **kwargs) -> None:
        self.by_workload = by_workload
        super().__init__(**kwargs)

    def exec_operation(self, data, workload_id) -> list:
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = { 'users': {} }

        before_grouping = []
        for item in data:
            dict_data: dict = json.loads(item)
            if dict_data["OwnerUserId"] in self.by_workload[workload_id]['users']:
                result = {
                    "OwnerUserId": dict_data["OwnerUserId"], 
                    "TotalScore": dict_data["TotalScore"] + self.by_workload[workload_id]['users'][dict_data["OwnerUserId"]]
                }

                before_grouping.append([ ( json.dumps(result), self.get_affinity(result) ) ])
            
            self.by_workload[workload_id]['users'][dict_data["OwnerUserId"]] = dict_data["TotalScore"]
        
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