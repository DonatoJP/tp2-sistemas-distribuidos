import pickle

class Task():
    def __init__(self, workload_id, data, centinel = False) -> None:
        self.workload_id = workload_id
        self.data = data
        self.centinel = centinel

    @classmethod
    def deserialize(cls, serialized_model: bytes):
        des = pickle.loads(serialized_model) 
        return cls(des["workload_id"], des["data"], des["centinel"])

    def serialize(self):
        obj_model = {}
        obj_model["workload_id"] = self.workload_id
        obj_model["data"] = self.data
        obj_model["centinel"] = self.centinel
        return pickle.dumps(obj_model)