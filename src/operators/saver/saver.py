import json
from io import StringIO
from ..operator import AbstractOperator
import os

from reviver.vault.client import VaultClient

class Saver(AbstractOperator):
    def __init__(self, column, key_save_name, **kwargs) -> None:
        self.column = column
        self.key = key_save_name
        rabbit_addr = os.getenv('RABBIT_ADDRESS')
        vault_input_queue_name = os.getenv('VAULT_INPUT_QUEUE_NAME')
        self.vault = VaultClient(rabbit_addr, vault_input_queue_name)
        super().__init__(**kwargs)

    def save_state(self, data: dict):
        result = {}
        result[self.column] = data[self.column]
        self.vault.post(self.key, result[self.column])
        return result

    def exec_operation(self, data) -> list:
        io_string = StringIO(data)
        result = map(lambda line: self.save_state(json.loads(line)), io_string)
        return list(map(lambda x: (json.dumps(x), self.get_affinity(x)), result))