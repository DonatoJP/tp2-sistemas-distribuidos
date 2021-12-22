import os
import logging
import signal
import time
import pickle
from threading import Condition, Lock, Event as THEvent
from bully.bully_manager import BullyManager

from connections_manager import ConnectionsManager
from bully import Bully, Event
from heartbeat import Heartbeat

from .server import RabbitMessageProcessor, RabbitConsumerServer
from .vault import Vault

logger = logging.getLogger("VaultMessageProcessor")
logging.basicConfig(format="[%(asctime)s]-%(levelname)s-%(name)s-%(message)s", level=logging.DEBUG, datefmt="%H:%M:%S")


class VaultMessageProcessor(RabbitMessageProcessor):
    def __init__(self, vault: Vault, retry_wait):
        self.vault = vault
        self.retry_wait = retry_wait

    def process(self, message):
        op, params = message.split(" ", 1)

        if op == "GET":
            queue, key = params.split(" ", 1)
            return queue, self._get(key)

        if op == "POST":
            key, value = params.split("=", 1)
            self._post(key, value)
            return None, None

        if op == "POST_KEY":
            key1, key2, value = params.split("=", 2)
            user_dict_value = self._get(key1)

            if len(user_dict_value) == 0:
                user_dict = dict()
            else:
                try:
                    user_dict = pickle.loads(bytes.fromhex(user_dict_value))
                except Exception as e:
                    logger.warning("Error %s =>  loading user dict value. Key1:  %s; Key2: %s; Value: %s, UserDictValue: %s", e, key1, key2, value, user_dict_value )
                    return None, None
                if not isinstance(user_dict, dict):
                    return None, None

            user_dict[key2] = value
            self._post(key1, pickle.dumps(user_dict).hex())

            return None, None

        if op == "GET_KEY":
            queue, keys = params.split(" ", 1)
            key1, key2 = keys.split("=", 1)
            user_dict_value = self._get(key1)

            # logging.info(f"GOT {user_dict_value}")

            if len(user_dict_value) == 0:
                return ""

            user_dict = pickle.loads(bytes.fromhex(user_dict_value))

            # logging.info(f"GOT DICT {user_dict}")

            if not isinstance(user_dict, dict):
                return ""

            value = user_dict.get(key2)

            return queue, value if value is not None else ""

    def _get(self, key) -> str:
        retry, value = self.vault.leader_get(key)
        while retry:
            time.sleep(self.retry_wait)
            retry, value = self.vault.leader_get(key)

        return value if value is not None else ""

    def _post(self, key, value):
        retry = self.vault.leader_post(key, value)
        while retry:
            time.sleep(self.retry_wait)
            retry = self.vault.leader_post(key, value)


def leader_start(server: RabbitConsumerServer):
    signal_exited = [False]

    def stop_signal_handler(*args):
        signal_exited[0] = True
        server.stop()

    signal.signal(signal.SIGTERM, stop_signal_handler)
    signal.signal(signal.SIGINT, stop_signal_handler)

    server.start()
    print("Shutting down server process")

    return signal_exited[0]


def follower_start(vault: Vault, leader_addr):
    signal_exited = [False]

    def stop_signal_handler(*args):
        signal_exited[0] = True
        vault.follower_stop()

    signal.signal(signal.SIGTERM, stop_signal_handler)
    signal.signal(signal.SIGINT, stop_signal_handler)

    vault.set_leader_addr(leader_addr)
    vault.follower_listen()

    return signal_exited[0]


def main():

    node_id = os.environ['NODE_ID']
    logger.info(f'Starting node {node_id}')

    event = THEvent()
    heartbeat = Heartbeat(event)
    heartbeat.start()

    vault_peers = [addr for addr in os.environ['VAULT_PEERS_INFO'].split(
        ',') if not addr.startswith(f"{node_id}-")]
    vault_port = os.environ['VAULT_LISTEN_PORT']
    vault_timeout = int(os.environ['VAULT_TIMEOUT'])
    vault_cm = ConnectionsManager(
        node_id, vault_port, vault_peers, vault_timeout)

    logger.info("Waiting for initialization...")

    logger.info("Initialization finished!")

    storage_path = os.environ['STORAGE_PATH']
    storage_buckets_number = int(os.environ['STORAGE_BUCKETS_NUMBER'])
    vault = Vault(vault_cm, storage_path, storage_buckets_number)

    retry_wait = float(os.environ['RETRY_WAIT'])

    message_processor = VaultMessageProcessor(vault, retry_wait)

    rabbit_adress = os.environ['RABBIT_ADDRESS']
    input_queue_name = os.environ['INPUT_QUEUE_NAME']

    server = RabbitConsumerServer(
        rabbit_adress, input_queue_name, message_processor)

    i_am_leader = [False]

    started = [False]
    started_cv = Condition(Lock())

    leader_elected = [False]
    leader_elected_cv = Condition(Lock())

    def new_leader_callback(bully: Bully):
        logger.info(f"CALLBACK {started[0]}")
        if not started[0]:
            # print("Before ACQ started_cv")
            started_cv.acquire()
            started[0] = True
            started_cv.notify_all()
            started_cv.release()

            logger.info(f"CALLBACK {started[0]}")

        else:
            logger.info(f"CALLBACK Started, checking leader {i_am_leader[0]}")
            if i_am_leader[0] and not bully.get_is_leader():
                logger.info(f'[NODE {node_id}] I was the leader. Now exiting')
                server.stop()
            elif not i_am_leader[0]:
                logger.info(f'[NODE {node_id}] I was follower. follower.stop()')
                vault.follower_stop()

        logger.info("CALLBACK Follower or server stopped")

        # print("Before ACQ leader_elected_cv")
        leader_elected_cv.acquire()
        leader_elected[0] = True
        leader_elected_cv.notify_all()
        leader_elected_cv.release()
        # print("After REL leader_elected_cv")

        logger.info("CALLBACK finished")

    # Este sleep es para asegurarnos de que cada nodo comience a aceptar conexiones en orden,
    # y no todos a la vez, lo cual genera errores
    time.sleep(3 * (int(node_id) - 1))

    bully_port = os.environ['BULLY_LISTEN_PORT']
    bully_peer_addrs = os.environ['BULLY_PEERS_INFO'].split(',')
    bully = BullyManager(node_id, bully_peer_addrs, bully_port, new_leader_callback)
    bully.start()


    started_cv.acquire()
    started_cv.wait_for(lambda: started[0])
    started_cv.release()

    exited = False
    while not exited:
        leader_elected_cv.acquire()
        leader_elected_cv.wait_for(lambda: leader_elected[0])
        leader_elected[0] = False
        leader_elected_cv.release()

        i_am_leader[0] = bully.get_is_leader()
        if i_am_leader[0]:
            logger.info(f"Leader Started: {exited}")
            exited = leader_start(server)
            logger.info(f"Leader finished: {exited}")
        else:
            logger.info(f"Follower Started: {exited}")
            leader_addr = bully.get_leader_addr()
            exited = follower_start(vault, leader_addr)
            logger.info(f"Follower finished: {exited}")

    vault_cm.shutdown_connections()
    event.set()

    heartbeat.join()
    bully._join_listen_thread()
    vault_cm._join_listen_thread()
