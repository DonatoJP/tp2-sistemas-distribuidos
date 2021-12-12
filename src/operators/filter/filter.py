import operator, json
from ..operator import AbstractOperator
from ..column_drop import ImportedOperator as ColumnDropOperator
from io import StringIO
from functools import reduce

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

        if op(to_filter, self.to_compare):
            return True
        
        return False
    
    def _make_filter_operation(self, line_data):
        data_dict = json.loads(line_data)
        meets_condition = self._filter_by_column(data_dict)
        if meets_condition:
            if len(self.keep_columns) > 0:
                processed_data = self.column_drop_operator.drop_columns(data_dict)
                return (json.dumps(processed_data), self.get_affinity(processed_data))
            else:
                return (json.dumps(line_data), self.get_affinity(line_data))
        
        return None

    
    def exec_operation(self, data) -> list:
        io_string = StringIO(data)
        res_aff_tuples = [ self._make_filter_operation(line) for line in io_string ]
        no_nones = list( filter(None, res_aff_tuples) )

        return self._group_by_ak(no_nones)



