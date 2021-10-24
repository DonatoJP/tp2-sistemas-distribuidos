import operator
from ..operator import AbstractOperator
from ..column_drop import ImportedOperator as ColumnDropOperator

class FilterOperator(AbstractOperator):
    def __init__(self) -> None:
        self.ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}
        self.column_drop_operator = ColumnDropOperator()
        super().__init__()
    
    def _filter_by_column(self, row: str, column_position = 0, to_compare = 10, op = '>'):
        op = self.ops[op]
        to_filter = float(row.split(',')[column_position])

        if operator.gt(to_filter, to_compare):
            return True
        
        return False
    
    def exec_operation(self, data, keep_columns=None, **kwargs) -> list:
        returnables = []
        result = self._filter_by_column(data, **kwargs)
        if result:
            if keep_columns:
                processed_data = self.column_drop_operator.drop_columns(data, keep_columns)
                returnables.append(processed_data)
            else:
                returnables.append(data)
        
        return returnables



