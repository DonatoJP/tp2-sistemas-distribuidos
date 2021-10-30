import importlib, sys, os, signal, json
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer


def main():
    module = os.environ['OPERATOR_MODULE']
    func_params = json.loads(os.environ['OPERATOR_PARAMS'])
    input_queue_name = os.environ['INPUT_QUEUE_NAME']
    output_queue_name = os.environ['OUTPUT_QUEUE_NAME']
    block_id = os.environ['BLOCK_ID']

    operation_module = importlib.import_module(module)
    ImportedOperator = getattr(operation_module, 'ImportedOperator')
    operator_to_use = ImportedOperator()

    queue_producer = QueueProducer()
    queue_producer.init_queue_pattern('work', output_queue_name)

    def callback_consuming_queue(ch, method, properties, body):
        decoded = body.decode('UTF-8')
        if decoded == 'END':
            print(f"{block_id} - Received END")
            queue_producer.send_end_centinel()
        else:
            returnables = operator_to_use.exec_operation(decoded, **func_params)
            print(f"{block_id} - {returnables}")
            for returnable in returnables:
                queue_producer.send(returnable)
    
    queue_consumer = QueueConsumer()
    queue_consumer.init_queue_pattern('work', 
        callback_consuming_queue, 
        queue_name=input_queue_name)
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        print("Closing server side socket")
        queue_consumer.close()
        queue_producer.close()
        sys.exit()

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
