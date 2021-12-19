import os, json

class ParseParametersError(Exception):
    def __init__(self, message, *args: object) -> None:
        self.message = f"The following parameter is mandatory: {message}"
        super().__init__(*args)

def parse_parameters():
    params = {}
    try:
        params["node_name"] = os.environ["NODE_NAME"]
        params["vault_queue_name"] = os.environ["VAULT_QUEUE_NAME"]
        params["module"] = os.environ['OPERATOR_MODULE']
        params["operator_params"] = json.loads(os.environ['OPERATOR_PARAMS'])
        params["input_queue_params"] = os.environ['INPUT_QUEUE_PARAMS']
        params["output_queue_params"] = os.environ['OUTPUT_QUEUE_PARAMS']
        params["centinels_to_receive"] = int(os.environ['CENTINELS_TO_RECEIVE'])
        params["centinels_to_send"] = int(os.environ['CENTINELS_TO_SEND'])
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
        params["centinels_to_receive"] = int(params["centinels_to_receive"])
        params["centinels_to_send"] = int(params["centinels_to_send"])
    except ValueError as e:
        raise ParseParametersError(f"'centinels_to_receive' and 'centinels_to_send' should be numbers")

    
    return params