from ..holder import AbstractHolder
import json

class TopNUsersHolder(AbstractHolder):
    name = 'top_n_users'

    def export_state(self):
        ret = super().export_state()
        ret["users_scores"] = self.users_scores
        ret["top_n"] = self.top_n
        return ret
    
    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, top_n, users_scores = [], **kwargs) -> None:
        self.users_scores = users_scores
        self.top_n = top_n
        super().__init__(perform_affinity=False, **kwargs)
    
    def exec_operation(self, data, **kwargs) -> list:
        for item in data:
            dict_data = json.loads(item)
            self.users_scores = self.users_scores + [(dict_data["OwnerUserId"], dict_data["TotalScore"])]
            self.users_scores.sort(key=lambda x: x[1], reverse=True)
            self.users_scores = self.users_scores[0:self.top_n]

    def _make_top_n(self):
        return self.users_scores

    def end(self):
        result = {"Result": self._make_top_n() }
        return [ ( json.dumps(result), self.get_affinity(result) ) ]