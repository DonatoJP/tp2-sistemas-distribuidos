import importlib, sys, os, signal, json
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit

def main():
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        print(e.message)
        exit()
    
    operation_module = importlib.import_module(params["module"])
    ImportedOperator = getattr(operation_module, 'ImportedOperator')
    operator_to_use = ImportedOperator()

    queue_producer = QueueProducer(params["next_step_count"])
    queue_consumer = QueueConsumer()

    queue_producer.init_queue_pattern('work', params["output_queue_name"])
    
    centinels_manager = CentinelsManager(params["previous_step_count"])
    block_id = params["block_id"]
    func_params = params["func_params"]

    def callback_consuming_queue(ch, method, properties, body):
        decoded = body.decode('UTF-8')
        if centinels_manager.is_centinel(decoded):
            print("Received Centinel")
            centinels_manager.count_centinel()
            if centinels_manager.are_all_received():
                print(f"{block_id} - Received all centinels. Stopping...")
                queue_producer.send_end_centinels(centinels_manager.centinel)
                exit([queue_consumer, queue_producer])

        else:
            returnables = operator_to_use.exec_operation(decoded, **func_params)
            print(f"{block_id} - {returnables}")
            for returnable in returnables:
                queue_producer.send(returnable)
    
    queue_consumer.init_queue_pattern('work', 
        callback_consuming_queue, 
        queue_name=params["input_queue_name"])
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        exit([queue_consumer, queue_producer], 0)

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
