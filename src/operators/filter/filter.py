import operator
from ..operator import AbstractOperator

class FilterOperator(AbstractOperator):
    def __init__(self) -> None:
        self.ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}
        super().__init__()
    
    def _filter_by_column(self, row: str, column_position = 0, to_compare = 10, op = '>'):
        op = self.ops[op]
        to_filter = float(row.split(',')[column_position])

        if operator.gt(to_filter, to_compare):
            return True
        
        return False
    
    def exec_operation(self, data, **kwargs) -> list:
        returnables = []
        result = self._filter_by_column(data, **kwargs)
        if result:
            returnables.append(data)
        
        return returnables



