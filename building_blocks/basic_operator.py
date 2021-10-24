import importlib, sys, os, signal, json
from rabbit_builders.consumers import basic_consumer

def main():
    module = os.environ['OPERATOR_MODULE']
    module_func = os.environ['OPERATOR_FUNC']
    func_params = json.loads(os.environ['OPERATOR_PARAMS'])
    queue_name = os.environ['INPUT_QUEUE_NAME']

    operation_module = importlib.import_module(module)
    func = getattr(operation_module, module_func)

    def callback_consuming_queue(ch, method, properties, body):
        result = func(str(body), **func_params)
        print(result)

    connection, channel = basic_consumer.build_basic_consumer(queue_name, callback_consuming_queue)
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        print("Closing server side socket")
        connection.close()
        sys.exit()

    signal.signal(signal.SIGTERM, __exit_gracefully)


    print('Starting to consume...')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
