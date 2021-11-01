import json
from io import StringIO
from ..operator import AbstractOperator
from ..column_drop.column_drop import DropColumnOperator

class ColumnDropTopicOperator(AbstractOperator):
    def __init__(self, columns_to_keep_by_topic, **kwargs) -> None:
        self.columns_to_keep_by_topic = columns_to_keep_by_topic
        super().__init__(**kwargs)

    def drop_columns(self, data):
        return self._drop_columns(data)
    
    def _build_output_by_topic(self, line: dict) -> list:
        result = []
        for key, value in self.columns_to_keep_by_topic.items():
            dropper = DropColumnOperator(value)
            result.append((json.dumps(dropper.drop_columns(line)), key))
        
        return result

    def exec_operation(self, data) -> list:
        io_string = StringIO(data)
        result = map(lambda line: self._build_output_by_topic(json.loads(line)), io_string)
        return [i for x in result for i in x]