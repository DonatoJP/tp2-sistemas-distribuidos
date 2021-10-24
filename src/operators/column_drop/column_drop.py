def drop_columns(line: str, keep_positions: list):
    line_splitted = line.split(',')
    result = []
    for position in keep_positions:
        result.append(line_splitted[position])

    return ','.join(result)