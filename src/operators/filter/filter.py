import operator, json
from ..operator import AbstractOperator
from ..column_drop import ImportedOperator as ColumnDropOperator

class FilterOperator(AbstractOperator):
    def __init__(self) -> None:
        self.ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}
        self.column_drop_operator = ColumnDropOperator()
        super().__init__()
    
    def _filter_by_column(self, data: dict, column: str, to_compare = 10, op = '>'):
        op = self.ops[op]
        to_filter = float(data[column])

        if operator.gt(to_filter, to_compare):
            return True
        
        return False
    
    def exec_operation(self, data, keep_columns=None, **kwargs) -> list:
        returnables = []
        data_dict = json.loads(data)
        meets_condition = self._filter_by_column(data_dict, **kwargs)
        if meets_condition:
            if keep_columns:
                processed_data = self.column_drop_operator.drop_columns(data_dict, keep_columns)
                returnables.append(json.dumps(processed_data))
            else:
                returnables.append(json.dumps(data))
        
        return returnables



