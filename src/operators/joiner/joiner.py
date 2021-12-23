from io import StringIO
import json, datetime
from ..operator import AbstractOperator

class Joiner(AbstractOperator):
    name = 'joiner-operator'

    @classmethod
    def from_state(cls, state: dict):
        return cls(**state)

    def __init__(self, by_workload={}, **kwargs) -> None:
        # self.waiting_answers = {}
        # self.waiting_questions = {}
        self.by_workload = by_workload
        super().__init__(**kwargs)
    
    def _parse_year(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').year
    
    def process_question(self, data: dict, workload_id) -> list:
        self.by_workload[workload_id]['waiting_questions'][data["Id"]] = data["Tags"] # Keep question tags for future answers
        data["Year"] = self._parse_year(data["CreationDate"])
        result = [ [ data ] ]
        if data["Id"] in self.by_workload[workload_id]['waiting_answers'].keys(): # If I had previous answers for this question
            for ans in self.by_workload[workload_id]['waiting_answers'][data["Id"]]:
                result.append(self.process_answer(ans, workload_id))
            del self.by_workload[workload_id]['waiting_answers'][data["Id"]]
        del data["Id"]
        del data["CreationDate"]
        return [item for sublist in result for item in sublist]
    
    def process_answer(self, data: dict, workload_id) -> list:
        if data["ParentId"] in self.by_workload[workload_id]['waiting_questions']: # If we have the corresponding question
            question_tags = self.by_workload[workload_id]['waiting_questions'][data["ParentId"]]
            result = {}
            result["Year"] = self._parse_year(data["CreationDate"])
            result["Score"] = data["Score"]
            result["Tags"] = question_tags
            return [ result ]
        else:
            if data["ParentId"] not in self.by_workload[workload_id]['waiting_answers']: # We keep a list of answers to process in the future
                self.by_workload[workload_id]['waiting_answers'][data["ParentId"]] = []

            self.by_workload[workload_id]['waiting_answers'][data["ParentId"]].append(data)
            return []
    
    def _process_line_of_chunk(self, line_data, workload_id) -> list:
        dict_data: dict = json.loads(line_data)
        if len(dict_data.keys()) == 3:
            return self.process_answer(dict_data, workload_id)
        else:
            return self.process_question(dict_data, workload_id)

    def exec_operation(self, data, workload_id) -> list:
        if workload_id not in self.by_workload:
            self.by_workload[workload_id] = { 'waiting_answers': {}, 'waiting_questions': {} }

        def operation(data):
            io_string = StringIO(data)
            res = [self._process_line_of_chunk(line, workload_id) for line in io_string]
            return [(json.dumps(x), self.get_affinity(x)) for i in res for x in i]

        return self._group_by_ak(operation(data))
    
    @classmethod
    def should_save_state(cls):
        return True
    
    @classmethod
    def should_track_duplicates(cls):
        return True
    
    def export_state(self):
        ret = super().export_state()
        ret['by_workload'] = self.by_workload
        return ret