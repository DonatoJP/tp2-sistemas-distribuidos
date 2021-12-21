import importlib, sys, os, signal, json, logging
import threading
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit
from reviver.workload import Task, DuplicatesManager
from reviver.heartbeat.heartbeat import Heartbeat
from reviver.state_saver import StateSaver


logging.basicConfig(format="[%(asctime)s]-%(levelname)s-%(name)s-%(message)s", level=logging.INFO, datefmt="%H:%M:%S")
logger = logging.getLogger("Basic Operator")

def main():
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        print(e.message)
        exit()

    exit_ev= threading.Event()
    heartbeat_t = Heartbeat(exit_ev)
    heartbeat_t.start()

    node_name = params["node_name"]
    state_saver = StateSaver("rabbitmq-tp2", params['vault_queue_name'])
    state = state_saver.retrieve_state(node_name)

    operation_module = importlib.import_module(params["module"])
    ImportedHolder = getattr(operation_module, 'ImportedHolder')

    queue_producer = QueueProducer(params["centinels_to_send"])
    queue_consumer = QueueConsumer()

    queue_producer.init_queue_pattern(**params["output_queue_params"])

    if state is None:
        centinels_manager = CentinelsManager(params["centinels_to_receive"])
        duplicates_manager = DuplicatesManager()
        holder_to_use = ImportedHolder(**params["operator_params"])
    else:
        duplicates_manager = DuplicatesManager.from_state(state[DuplicatesManager.name])
        centinels_manager = CentinelsManager.from_state(state[CentinelsManager.name])
        holder_to_use = ImportedHolder.from_state(state[ImportedHolder.name])
    
    print(holder_to_use)

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
                holder_to_use.exec_operation(task.data, task.workload_id)
            
            duplicates_manager.register_task(task)

            # TODO: Integrar Vault para guardar estado
            state_saver.save_state(node_name, [duplicates_manager, centinels_manager, holder_to_use])

        ch.basic_ack(method.delivery_tag)

    params["input_queue_params"]["callback"] = callback_consuming_queue
    queue_consumer.init_queue_pattern(**params["input_queue_params"])
    
    def __exit_gracefully(*args):
        print("Received SIGTERM signal. Starting graceful exit...")
        exit_ev.set()
        exit([queue_consumer])

    signal.signal(signal.SIGTERM, __exit_gracefully)

    print('Starting to consume...')
    try:
        queue_consumer.start_consuming()
    except Exception as e:
        logger.warning("Recieved Excetion %s", e)
        exit_ev.set()
        exit([queue_consumer, queue_producer], 0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)

        except SystemExit:
            os._exit(0)
