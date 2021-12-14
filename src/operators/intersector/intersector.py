import json, datetime
from ..operator import AbstractOperator

class Intersector(AbstractOperator):
    def __init__(self, **kwargs) -> None:
        self.users = {}
        super().__init__(**kwargs)

    def exec_operation(self, data) -> list:
        before_grouping = []
        for item in data:
            dict_data: dict = json.loads(item)
            if dict_data["OwnerUserId"] in self.users.keys():
                result = {
                    "OwnerUserId": dict_data["OwnerUserId"], 
                    "TotalScore": dict_data["TotalScore"] + self.users[dict_data["OwnerUserId"]]
                }

                before_grouping.append([ ( json.dumps(result), self.get_affinity(result) ) ])
            
            self.users[dict_data["OwnerUserId"]] = dict_data["TotalScore"]
        
        before_grouping = [tup for item in before_grouping for tup in item]
        return self._group_by_ak(before_grouping)
