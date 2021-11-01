from io import StringIO
import json, datetime
from ..operator import AbstractOperator

class Joiner(AbstractOperator):
    def __init__(self, **kwargs) -> None:
        self.waiting_answers = {}
        self.waiting_questions = {}
        super().__init__(**kwargs)
    
    def _parse_year(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').year
    
    def process_question(self, data: dict) -> list:
        self.waiting_questions[data["Id"]] = data["Tags"] # Keep question tags for future answers
        data["Year"] = self._parse_year(data["CreationDate"])
        result = [ [ data ] ]
        if data["Id"] in self.waiting_answers.keys(): # If I had previous answers for this question
            for ans in self.waiting_answers[data["Id"]]:
                result.append(self.process_answer(ans))
            del self.waiting_answers[data["Id"]]
        del data["Id"]
        del data["CreationDate"]
        return [item for sublist in result for item in sublist]
    
    def process_answer(self, data: dict) -> list:
        if data["ParentId"] in self.waiting_questions.keys(): # If we have the corresponding question
            question_tags = self.waiting_questions[data["ParentId"]]
            result = {}
            result["Year"] = self._parse_year(data["CreationDate"])
            result["Score"] = data["Score"]
            result["Tags"] = question_tags
            return [ result ]
        else:
            if data["ParentId"] not in self.waiting_answers: # We keep a list of answers to process in the future
                self.waiting_answers[data["ParentId"]] = []

            self.waiting_answers[data["ParentId"]].append(data)
            return []
    
    def _process_line_of_chunk(self, line_data) -> list:
        dict_data: dict = json.loads(line_data)
        if len(dict_data.keys()) == 3:
            return self.process_answer(dict_data)
        else:
            return self.process_question(dict_data)

    def exec_operation(self, data) -> list:
        io_string = StringIO(data)
        res = [self._process_line_of_chunk(line) for line in io_string]

        return [(json.dumps(x), self.get_affinity(x)) for i in res for x in i]