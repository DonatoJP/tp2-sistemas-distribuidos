import json
from ..operator import AbstractOperator

class DropColumnOperator(AbstractOperator):
    def __init__(self) -> None:
        super().__init__()

    def _drop_columns(self, data: dict, columns_to_keep: list):
        result = {}
        for column in columns_to_keep:
            result[column] = data[column]

        return result

    def drop_columns(self, data, columns_to_keep):
        return self._drop_columns(data, columns_to_keep)

    def exec_operation(self, data, **kwargs) -> list:
        data_dict = json.loads(data)
        result = self._drop_columns(data_dict, **kwargs)
        return [ json.dumps(result) ]