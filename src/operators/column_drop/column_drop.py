import json
from io import StringIO
from ..operator import AbstractOperator

class DropColumnOperator(AbstractOperator):
    name = 'drop-column-operator'

    @classmethod
    def from_state(cls, state: dict):
        return cls()

    def __init__(self, columns_to_keep, **kwargs) -> None:
        self.columns_to_keep = columns_to_keep
        super().__init__(**kwargs)

    def _drop_columns(self, data: dict):
        result = {}
        for column in self.columns_to_keep:
            result[column] = data[column]

        return result

    def drop_columns(self, data):
        return self._drop_columns(data)

    def exec_operation(self, data, workload_id) -> list:
        io_string = StringIO(data)
        result = map(lambda line: self._drop_columns(json.loads(line)), io_string)
        return list(map(lambda x: (json.dumps(x), self.get_affinity(x)), result))
    
    @classmethod
    def should_save_state(cls):
        return False
    
    @classmethod
    def should_track_duplicates(cls):
        return False

    def export_state(self):
        return None