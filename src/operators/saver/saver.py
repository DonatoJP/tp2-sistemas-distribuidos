import json
from io import StringIO
from ..operator import AbstractOperator
import os

from reviver.vault.client import VaultClient

class Saver(AbstractOperator):
    name = 'saver-operator'

    @classmethod
    def from_state(cls, state: dict):
        return cls()

    def __init__(self, column, key_save_name, **kwargs) -> None:
        self.column = column
        self.key = key_save_name
        rabbit_addr = os.getenv('RABBIT_ADDRESS')
        vault_input_queue_name = os.getenv('VAULT_INPUT_QUEUE_NAME')
        self.vault = VaultClient(rabbit_addr, vault_input_queue_name)
        super().__init__(**kwargs)

    def save_state(self, data: dict, workload_id):
        result = {}
        result[self.column] = data
        self.vault.post(f"{self.key}-{workload_id}", result[self.column])
        return result

    def exec_operation(self, data, workload_id) -> list:
        io_string = StringIO(data)
        result = map(lambda line: self.save_state(json.loads(line), workload_id), io_string)
        return list(map(lambda x: (json.dumps(x), self.get_affinity(x)), result))
    
    @classmethod
    def should_save_state(cls):
        return False
    
    @classmethod
    def should_track_duplicates(cls):
        return False

    def export_state(self):
        return None