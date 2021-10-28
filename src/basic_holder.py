import importlib, sys, os, signal, json
from rabbit_builders.consumers import QueueConsumer

def main():
    module = os.environ['OPERATOR_MODULE']
    func_params = json.loads(os.environ['OPERATOR_PARAMS'])
    input_queue_name = os.environ['INPUT_QUEUE_NAME']

    operation_module = importlib.import_module(module)
    ImportedHolder = getattr(operation_module, 'ImportedHolder')
    holder_to_use = ImportedHolder()

    def callback_consuming_queue(ch, method, properties, body):
        decoded = body.decode('UTF-8')
        if decoded == 'END':
            result = holder_to_use.end()
            print(result)
        else:
            holder_to_use.exec_operation(decoded, **func_params)

    queue_consumer = QueueConsumer()
    queue_consumer.init_queue_pattern('work',
        callback_consuming_queue,
        queue_name=input_queue_name)
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        print("Closing server side socket")
        queue_consumer.close()
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
