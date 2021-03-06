from ..holder import AbstractHolder
import json

class TopNYearsHolder(AbstractHolder):
    def __init__(self, top_n, **kwargs) -> None:
        self.group_by_year = {}
        self.top_n = top_n
        super().__init__(**kwargs)
    
    def exec_operation(self, data, **kwargs) -> list:
        dict_data = json.loads(data)
        if dict_data["Year"] not in self.group_by_year.keys():
            self.group_by_year[dict_data["Year"]] = {}
        
        if not dict_data["Tags"]:
            return

        tags = dict_data["Tags"].split(' ')
        for tag in tags:
            if tag not in self.group_by_year[dict_data["Year"]].keys():
                self.group_by_year[dict_data["Year"]][tag] = 0
            self.group_by_year[dict_data["Year"]][tag] += int(dict_data["Score"])
    
    def _make_top_n(self, year):
        tags = self.group_by_year[year]
        tags_tuple_list = list(tags.items())
        tags_tuple_list.sort(key=lambda x: x[1], reverse=True)
        return tags_tuple_list[0:self.top_n]

    def end(self):
        result = {}
        for year in self.group_by_year.keys():
            result[year] = self._make_top_n(year)
        return [ (json.dumps(result), self.get_affinity(result)) ]