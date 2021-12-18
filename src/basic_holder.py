import importlib, sys, os, signal, json
import threading
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit
from utils.workload import Task, DuplicatesManager
from reviver.heartbeat.heartbeat import Heartbeat

def main():
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        print(e.message)
        exit()

    exit_ev= threading.Event()
    heartbeat_t = Heartbeat(exit_ev)
    heartbeat_t.start()

    operation_module = importlib.import_module(params["module"])
    ImportedHolder = getattr(operation_module, 'ImportedHolder')
    holder_to_use = ImportedHolder(**params["operator_params"])

    queue_producer = QueueProducer(params["centinels_to_send"])
    queue_consumer = QueueConsumer()

    queue_producer.init_queue_pattern(**params["output_queue_params"])

    centinels_manager = CentinelsManager(params["centinels_to_receive"])
    duplicates_manager = DuplicatesManager()

    def callback_consuming_queue(ch, method, properties, body):
        task = Task.deserialize(body)

        if not duplicates_manager.is_duplicate(task):
            if centinels_manager.is_centinel(task):
                centinels_manager.count_centinel(task)
                if centinels_manager.are_all_received(task):
                    result = holder_to_use.end()
                    for returnable in result:
                        new_task = Task(task.workload_id, returnable[0])
                        queue_producer.send(new_task.serialize(), returnable[1])

                    print(f"Received all centinels for workload {task.workload_id}.")
                    queue_producer.send_end_centinels(
                        centinels_manager.build_centinel(task)
                    )
            else:
                holder_to_use.exec_operation(task.data)
            
            duplicates_manager.register_task(task)

        ch.basic_ack(method.delivery_tag)

    params["input_queue_params"]["callback"] = callback_consuming_queue
    queue_consumer.init_queue_pattern(**params["input_queue_params"])
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        exit_ev.set()
        exit([queue_consumer])

    signal.signal(signal.SIGTERM, __exit_gracefully)

    print('Starting to consume...')
    queue_consumer.start_consuming()
    exit_ev.set()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)

        except SystemExit:
            os._exit(0)
