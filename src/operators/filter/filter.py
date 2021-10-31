import operator, json
from ..operator import AbstractOperator
from ..column_drop import ImportedOperator as ColumnDropOperator

class FilterOperator(AbstractOperator):
    def __init__(self, column, keep_columns=[], to_compare=10, op='<', **kwargs) -> None:
        self.ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}
        self.op = self.ops[op]
        self.column = column
        self.to_compare = to_compare
        self.keep_columns = keep_columns
        self.column_drop_operator = ColumnDropOperator(keep_columns, **kwargs)
        super().__init__(**kwargs)
    
    def _filter_by_column(self, data: dict):
        op = self.op
        to_filter = float(data[self.column])

        if operator.gt(to_filter, self.to_compare):
            return True
        
        return False
    
    def exec_operation(self, data) -> list:
        returnables = []
        data_dict = json.loads(data)
        meets_condition = self._filter_by_column(data_dict)
        if meets_condition:
            if len(self.keep_columns) > 0:
                processed_data = self.column_drop_operator.drop_columns(data_dict)
                returnables.append((json.dumps(processed_data), self.get_affinity(processed_data)))
            else:
                returnables.append((json.dumps(data), self.get_affinity(data)))
        
        return returnables



