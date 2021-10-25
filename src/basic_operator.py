import importlib, sys, os, signal, json
from rabbit_builders.consumers import basic_consumer
from rabbit_builders.producers import basic_producer

def main():
    module = os.environ['OPERATOR_MODULE']
    func_params = json.loads(os.environ['OPERATOR_PARAMS'])
    input_queue_name = os.environ['INPUT_QUEUE_NAME']
    output_queue_name = os.environ['OUTPUT_QUEUE_NAME']

    operation_module = importlib.import_module(module)
    ImportedOperator = getattr(operation_module, 'ImportedOperator')
    operator_to_use = ImportedOperator()

    output_connection, output_channel = basic_producer.build_basic_producer(output_queue_name)


    def callback_consuming_queue(ch, method, properties, body):
        decoded = body.decode('UTF-8')
        if decoded == 'END':
            output_channel.basic_publish(exchange='',
                                     routing_key=output_queue_name,
                                     body='END')
        else:
            returnables = operator_to_use.exec_operation(decoded, **func_params)
            print(returnables)
            for returnable in returnables:
                output_channel.basic_publish(exchange='',
                                        routing_key=output_queue_name,
                                        body=returnable)

    input_connection, input_channel = basic_consumer.build_basic_consumer(input_queue_name, callback_consuming_queue)
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        print("Closing server side socket")
        input_connection.close()
        output_connection.close()
        sys.exit()

    signal.signal(signal.SIGTERM, __exit_gracefully)


    print('Starting to consume...')
    input_channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
