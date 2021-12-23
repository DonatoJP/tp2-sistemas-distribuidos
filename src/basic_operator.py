import importlib, sys, os, signal, json, logging
from rabbit_builders.consumers import QueueConsumer
from rabbit_builders.producers import QueueProducer
from rabbit_builders.centinels_manager import CentinelsManager
from utils import parse_parameters, ParseParametersError, exit
from reviver.workload import Task, DuplicatesManager
from reviver.heartbeat.heartbeat import Heartbeat
import threading
from reviver.state_saver import StateSaver
from reviver.log import create_logger

logger = create_logger('basic-operator')

def main():
    # logging.basicConfig(format="[%(asctime)s]-%(levelname)s-%(name)s-%(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    try:
        params = parse_parameters()
    except ParseParametersError as e:
        logger.warning(e.message)
        exit()
    event = threading.Event()

    heartbeat_t = Heartbeat(event)
    heartbeat_t.start()

    node_name = params["node_name"]
    state_saver = StateSaver("rabbitmq-tp2", params['vault_queue_name'])
    state = state_saver.retrieve_state(node_name)

    operation_module = importlib.import_module(params["module"])
    ImportedOperator = getattr(operation_module, 'ImportedOperator')
    
    queue_producer = QueueProducer(params["centinels_to_send"])
    queue_consumer = QueueConsumer()

    queue_producer.init_queue_pattern(**params["output_queue_params"])

    duplicates_manager = None
    
    if state is None:
        centinels_manager = CentinelsManager(params["centinels_to_receive"])
        operator_to_use = ImportedOperator(**params['operator_params'])
    else:
        centinels_manager = CentinelsManager.from_state(state[CentinelsManager.name])
        if ImportedOperator.should_save_state():
            operator_to_use = ImportedOperator.from_state(state[ImportedOperator.name])
        else:
            operator_to_use = ImportedOperator(**params['operator_params'])

    if ImportedOperator.should_track_duplicates():
        if state is not None and DuplicatesManager.name in state:
            duplicates_manager = DuplicatesManager.from_state(state[DuplicatesManager.name])
        else:
            duplicates_manager = DuplicatesManager()
    
    logger.debug(centinels_manager)
    logger.debug(operator_to_use)

    def callback_consuming_queue(ch, method, properties, body):
        task = Task.deserialize(body)

        if centinels_manager.is_centinel(task):
            logger.debug("Received Centinel")
            centinels_manager.count_centinel(task)
            if centinels_manager.are_all_received(task):
                logger.debug(f"Received all centinels for workload {task.workload_id}.")
                queue_producer.send_end_centinels(
                    centinels_manager.build_centinel(task),
                    operator_to_use.get_all_routing_keys()
                )

        else:
            returnables = operator_to_use.exec_operation(task.data, task.workload_id)
            for returnable in returnables:

                # returnable = (task_data, routing_key)
                new_task = Task(task.workload_id, returnable[0], task_id=task.task_id)
                queue_producer.send(new_task.serialize(), returnable[1])
        
        # TODO: Integrar con vault
        if ImportedOperator.should_save_state():
            if ImportedOperator.should_track_duplicates():
                state_saver.save_state(node_name, [ operator_to_use, centinels_manager, duplicates_manager ])
            else:
                state_saver.save_state(node_name, [ operator_to_use, centinels_manager ])
        else:
            state_saver.save_state(node_name, [ centinels_manager ])
        
        ch.basic_ack(method.delivery_tag)
    
    params["input_queue_params"]["callback"] = callback_consuming_queue
    queue_consumer.init_queue_pattern(**params["input_queue_params"])
    
    def __exit_gracefully(*args):
        logger.warning("Received SIGTERM signal. Starting graceful exit...")
        event.set()
        exit([queue_consumer, queue_producer], 0)

    signal.signal(signal.SIGTERM, __exit_gracefully)

    logger.debug('Starting to consume...')
    try:
        queue_consumer.start_consuming()
    except Exception as e:
        logger.warning("Recieved Excetion %s", e)
        event.set()
        exit([queue_consumer, queue_producer], 0)




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.debug('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
