import os, json

class ParseParametersError(Exception):
    def __init__(self, message, *args: object) -> None:
        self.message = f"The following parameter is mandatory: {message}"
        super().__init__(*args)

def parse_parameters():
    params = {}
    try:
        params["module"] = os.environ['OPERATOR_MODULE']
        params["func_params"] = json.loads(os.environ['OPERATOR_PARAMS'])
        params["input_queue_params"] = os.environ['INPUT_QUEUE_PARAMS']
        params["output_queue_params"] = os.environ['OUTPUT_QUEUE_PARAMS']
        params["block_id"] = os.environ['BLOCK_ID']
        params["previous_step_count"] = int(os.environ['PREVIOUS_STEP_COUNT'])
        params["next_step_count"] = int(os.environ['NEXT_STEP_COUNT'])
    except KeyError as e:
        raise ParseParametersError(f"The following parameter is mandatory: {e}")

    try:
        params["output_queue_params"] = json.loads(params["output_queue_params"])
    except:
        raise ParseParametersError(f"output_queue_params must be json")

    try:
        params["input_queue_params"] = json.loads(params["input_queue_params"])
    except:
        raise ParseParametersError(f"input_queue_params must be json")
    
    try:
        params["previous_step_count"] = int(params["previous_step_count"])
        params["next_step_count"] = int(params["next_step_count"])
    except ValueError as e:
        raise ParseParametersError(f"'previous_step_count' and 'next_step_count' should be numbers")

    
    return params