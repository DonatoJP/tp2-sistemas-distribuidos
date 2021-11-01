import json
from io import StringIO
from ..operator import AbstractOperator
from ..column_drop.column_drop import DropColumnOperator

class ColumnDropTopicOperator(AbstractOperator):
    def __init__(self, params_by_topic, perform_affinity, max_affinity) -> None:
        self.params_by_topic: dict = params_by_topic
        self.perform_affinity = perform_affinity
        self.max_affinity = max_affinity

    def drop_columns(self, data):
        return self._drop_columns(data)
    
    def _build_output_by_topic(self, line: dict) -> list:
        result = []
        for key, value in self.params_by_topic.items():
            dropper = DropColumnOperator(**value)
            aff = dropper.get_affinity(line)
            rk = key if aff == '' else f"{key}.{aff}"
            result.append((json.dumps(dropper.drop_columns(line)), rk))
        
        return result

    def get_all_routing_keys(self):
        topic_wo_aff = self.params_by_topic.keys()
        if not self.perform_affinity:
            return topic_wo_aff
        
        return [f"{topic}.{aff}" for topic in topic_wo_aff for aff in range(0, self.max_affinity)]

    def exec_operation(self, data) -> list:
        io_string = StringIO(data)
        result = map(lambda line: self._build_output_by_topic(json.loads(line)), io_string)
        return [i for x in result for i in x]