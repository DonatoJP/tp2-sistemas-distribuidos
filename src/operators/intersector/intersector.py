import json, datetime
from ..operator import AbstractOperator

class Intersector(AbstractOperator):
    def __init__(self, **kwargs) -> None:
        self.users = {}
        super().__init__(**kwargs)

    def exec_operation(self, data) -> list:
        dict_data: dict = json.loads(data)
        if dict_data["OwnerUserId"] in self.users.keys():
            result = {
                "OwnerUserId": dict_data["OwnerUserId"], 
                "TotalScore": dict_data["TotalScore"] + self.users[dict_data["OwnerUserId"]]
            }

            return [ ( json.dumps(result), self.get_affinity(result) ) ]
        
        self.users[dict_data["OwnerUserId"]] = dict_data["TotalScore"]
        return []