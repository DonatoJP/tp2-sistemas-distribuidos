from ..holder import AbstractHolder
import json

class TopNYearsHolder(AbstractHolder):
    name = 'top_n_years'

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
            self.by_workload[workload_id] = {'group_by_year': {}}

        for item in data:
            dict_data = json.loads(item)
            if dict_data["Year"] not in self.by_workload[workload_id]['group_by_year'].keys():
                self.by_workload[workload_id]['group_by_year'][dict_data["Year"]] = {}
            
            if not dict_data["Tags"]:
                return

            tags = dict_data["Tags"].split(' ')
            for tag in tags:
                if tag not in self.by_workload[workload_id]['group_by_year'][dict_data["Year"]].keys():
                    self.by_workload[workload_id]['group_by_year'][dict_data["Year"]][tag] = 0
                self.by_workload[workload_id]['group_by_year'][dict_data["Year"]][tag] += int(dict_data["Score"])
    
    def _make_top_n(self, year, workload_id):
        tags = self.by_workload[workload_id]['group_by_year'][year]
        tags_tuple_list = list(tags.items())
        tags_tuple_list.sort(key=lambda x: x[1], reverse=True)
        return tags_tuple_list[0:self.top_n]

    def end(self, workload_id):
        result = {}
        for year in self.by_workload[workload_id]['group_by_year'].keys():
            result[year] = self._make_top_n(year, workload_id)
        return [ (json.dumps(result), self.get_affinity(result)) ]