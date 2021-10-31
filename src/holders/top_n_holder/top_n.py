from ..holder import AbstractHolder
import json

class TopNHolder(AbstractHolder):
    def __init__(self, top_n, **kwargs) -> None:
        self.group_by_year = {}
        self.top_n = top_n
        super().__init__()
    
    def exec_operation(self, data, **kwargs) -> list:
        dict_data = json.loads(data)
        if dict_data["Year"] not in self.group_by_year.keys():
            self.group_by_year[dict_data["Year"]] = {}
        
        tags = dict_data["Tags"].split(' ')
        for tag in tags:
            if tag not in self.group_by_year[dict_data["Year"]].keys():
                self.group_by_year[dict_data["Year"]][tag] = 0
            self.group_by_year[dict_data["Year"]][tag] += dict_data["Score"]
    
    def _make_top_n(self, year):
        tags = self.group_by_year[year]
        tags_tuple_list = list(tags.items())
        tags_tuple_list.sort(key=lambda x: x[1], reverse=True)
        return tags_tuple_list[0:self.top_n]

    def end(self):
        return [(year, self._make_top_n(year)) for year in self.group_by_year.keys()]