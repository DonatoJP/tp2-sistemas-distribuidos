import json
from io import StringIO
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
        io_string = StringIO(data)
        result = map(lambda line: self._drop_columns(json.loads(line), **kwargs), io_string)
        return list(map(lambda x: json.dumps(x), result))