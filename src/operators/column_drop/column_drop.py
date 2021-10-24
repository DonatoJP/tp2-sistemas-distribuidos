from ..operator import AbstractOperator

class DropColumnOperator(AbstractOperator):
    def __init__(self) -> None:
        super().__init__()

    def _drop_columns(self, line: str, keep_positions: list):
        line_splitted = line.split(',')
        result = []
        for position in keep_positions:
            result.append(line_splitted[position])

        return ','.join(result)

    def drop_columns(self, line, keep_positions):
        return self._drop_columns(line, keep_positions)

    def exec_operation(self, data, **kwargs) -> list:
        return [ self._drop_columns(data, **kwargs) ]