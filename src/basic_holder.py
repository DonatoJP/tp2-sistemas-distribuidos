import importlib, sys, os, signal, json
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit

def main():
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        print(e.message)
        exit()

    operation_module = importlib.import_module(params["module"])
    ImportedHolder = getattr(operation_module, 'ImportedHolder')
    holder_to_use = ImportedHolder(**params["operator_params"])

    queue_consumer = QueueConsumer()

    centinels_manager = CentinelsManager(params["previous_step_count"])

    def callback_consuming_queue(ch, method, properties, body):
        decoded = body.decode('UTF-8')
        if centinels_manager.is_centinel(decoded):
            centinels_manager.count_centinel()
            if centinels_manager.are_all_received():
                result = holder_to_use.end()
                print(result)
                exit([queue_consumer])
        else:
            holder_to_use.exec_operation(decoded)

    params["input_queue_params"]["callback"] = callback_consuming_queue
    queue_consumer.init_queue_pattern(**params["input_queue_params"])
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        exit([queue_consumer])

    signal.signal(signal.SIGTERM, __exit_gracefully)


    print('Starting to consume...')
    queue_consumer.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
