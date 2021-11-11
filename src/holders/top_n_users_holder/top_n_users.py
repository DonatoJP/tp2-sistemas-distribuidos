from ..holder import AbstractHolder
import json

class TopNUsersHolder(AbstractHolder):
    def __init__(self, top_n, **kwargs) -> None:
        self.users_scores = []
        self.top_n = top_n
        super().__init__(perform_affinity=False, **kwargs)
    
    def exec_operation(self, data, **kwargs) -> list:
        dict_data = json.loads(data)
        self.users_scores = self.users_scores + [(dict_data["OwnerUserId"], dict_data["TotalScore"])]
        self.users_scores.sort(key=lambda x: x[1], reverse=True)
        self.users_scores = self.users_scores[0:self.top_n]
        # self.users_scores[dict_data["OwnerUserId"]] = dict_data["TotalScore"]
    
    # def _make_top_n(self):
    #     users_scores = list(self.users_scores.items())
    #     users_scores.sort(key=lambda x: x[1], reverse=True)
    #     return users_scores[0:self.top_n]

    def _make_top_n(self):
        return self.users_scores

    def end(self):
        result = {"Result": self._make_top_n() }
        return [ ( json.dumps(result), self.get_affinity(result) ) ]