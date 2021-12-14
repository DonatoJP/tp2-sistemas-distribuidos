import importlib, sys, os, signal, json
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit
from utils.workload import Task
from reviver.heartbeat.heartbeat import Heartbeat
import threading

def main():
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        print(e.message)
        exit()
    event = threading.Event()

    heartbeat_t = Heartbeat(event)
    heartbeat_t.start()

    operation_module = importlib.import_module(params["module"])
    ImportedOperator = getattr(operation_module, 'ImportedOperator')
    operator_to_use = ImportedOperator(**params['operator_params'])

    queue_producer = QueueProducer(params["centinels_to_send"])
    queue_consumer = QueueConsumer()

    queue_producer.init_queue_pattern(**params["output_queue_params"])
    
    centinels_manager = CentinelsManager(params["centinels_to_receive"])
    block_id = 1

    def callback_consuming_queue(ch, method, properties, body):
        finish = False
        task = Task.deserialize(body)

        if centinels_manager.is_centinel(task):
            print("Received Centinel")
            centinels_manager.count_centinel(task)
            if centinels_manager.are_all_received(task):
                print(f"{block_id} - Received all centinels. Stopping...")
                queue_producer.send_end_centinels(
                    centinels_manager.build_centinel(task),
                    operator_to_use.get_all_routing_keys()
                )
                finish = True

        else:
            returnables = operator_to_use.exec_operation(task.data)
            for returnable in returnables:
                print(f"{block_id} - {returnable}")

                # returnable = (task_data, routing_key)
                new_task = Task(task.workload_id, returnable[0])
                queue_producer.send(new_task.serialize(), returnable[1])
        
        ch.basic_ack(method.delivery_tag)
        if finish:
            event.set()
            exit([queue_consumer, queue_producer])
    
    params["input_queue_params"]["callback"] = callback_consuming_queue
    queue_consumer.init_queue_pattern(**params["input_queue_params"])
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        event.set()
        exit([queue_consumer, queue_producer], 0)

    signal.signal(signal.SIGTERM, __exit_gracefully)

    print('Starting to consume...')
    queue_consumer.start_consuming()
    event.set()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
