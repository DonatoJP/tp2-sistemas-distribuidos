import pickle, uuid, base64

class Task():
    def __init__(self, workload_id, data, centinel = False, task_id = None) -> None:
        if task_id is None:
            self.task_id = str(uuid.uuid4())
        else:
            self.task_id = task_id

        self.workload_id = workload_id
        self.data = data
        self.centinel = centinel

    @classmethod
    def deserialize(cls, serialized_model: bytes):
        try:
            des = pickle.loads(serialized_model) 
            return cls(des["workload_id"], des["data"], des["centinel"], des["task_id"])
        except:
            des = base64.b64decode(serialized_model) # Necesary if we copy-paste messages in RabbitMQ Admin
            des = pickle.loads(des)
            return cls(des["workload_id"], des["data"], des["centinel"], des["task_id"])

    def serialize(self):
        obj_model = {}
        obj_model["workload_id"] = self.workload_id
        obj_model["data"] = self.data
        obj_model["centinel"] = self.centinel
        obj_model["task_id"] = self.task_id
        return pickle.dumps(obj_model)