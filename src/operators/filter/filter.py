import operator
ops = {">": operator.gt, "<": operator.lt, ">=": operator.ge, "<=": operator.le}
def filter_by_column(row: str, column_position = 0, to_compare = 10, op = '>'):
    op = ops[op]
    to_filter = float(row.split(',')[column_position])

    if operator.gt(to_filter, to_compare):
        return row
    
    return None