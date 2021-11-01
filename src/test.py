from operators.column_drop_topics import ImportedOperator as CDT

config = {
    "params_by_topic": {
        "topic1": {
            "columns_to_keep": [
                "Score"
            ],
            "perform_affinity": True,
            "affinity_key": "Score",
            "affinity_divider": 2
        },
        "topic2": {
            "columns_to_keep": [
                "OwnerId"
            ],
            "perform_affinity": True,
            "affinity_key": "OwnerId",
            "affinity_divider": 2
        },
        "topic3": {
            "columns_to_keep": [
                "Id"
            ],
            "perform_affinity": True,
            "affinity_key": "Id",
            "affinity_divider": 3
        }
    },
    "perform_affinity": True,
    "max_affinity": 3
}

input = '{"Id": 1, "OwnerId":5, "Score": 10}\n{"Id": 2, "OwnerId":6, "Score": -10}\n{"Id": 3, "OwnerId":8, "Score": 21}'

cdt = CDT(**config)

aux = cdt.exec_operation(input)

