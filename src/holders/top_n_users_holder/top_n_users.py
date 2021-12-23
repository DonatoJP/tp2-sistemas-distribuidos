from ..holder import AbstractHolder
import json

class TopNUsersHolder(AbstractHolder):
    name = 'top_n_users'

    def export_state(self):
        ret = super().export_state()
        ret["by_workload"] = self.by_workload
        ret["top_n"] = self.top_n
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, top_n, by_workload = {}, **kwargs) -> None:
        self.by_workload = by_workload
        self.top_n = top_n
        super().__init__(**kwargs)
    
    def exec_operation(self, data, workload_id) -> list:
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = {'users_scores': []}

        for item in data:
            dict_data = json.loads(item)
            self.by_workload[workload_id]['users_scores'] = self.by_workload[workload_id]['users_scores'] + [(dict_data["OwnerUserId"], dict_data["TotalScore"])]
            self.by_workload[workload_id]['users_scores'].sort(key=lambda x: x[1], reverse=True)
            self.by_workload[workload_id]['users_scores'] = self.by_workload[workload_id]['users_scores'][0:self.top_n]

    def _make_top_n(self, workload_id):
        return self.by_workload[workload_id]['users_scores']

    def end(self, workload_id):
        if workload_id not in self.by_workload:
            result = {"Result": []}
        else:
            result = {"Result": self._make_top_n(workload_id) }
        return [ ( json.dumps(result), self.get_affinity(result) ) ]