import pickle

class Task():
    def __init__(self, workload_id, data) -> None:
        self.workload_id = workload_id
        self.data = data

    @classmethod
    def deserialize(serialized_model: bytes):
        des = pickle.loads(serialized_model) 
        return Task(des["workload_id"], des["data"])

    def serialize(self):
        obj_model = {}
        obj_model["workload_id"] = self.workload_id
        obj_model["data"] = self.data
        return pickle.dumps(obj_model)