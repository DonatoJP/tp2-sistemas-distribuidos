import os
import logging
import signal
import time
from threading import Condition, Lock, Event as THEvent
from bully.bully_manager import BullyManager, Event

from connections_manager import ConnectionsManager

from .server import RabbitMessageProcessor, RabbitConsumerServer
from .vault import Vault


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

    def _get(self, key):
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
    logging.basicConfig(level="INFO")

    node_id = os.environ['NODE_ID']
    logging.info(f'Starting node {node_id}')

    bully_port = os.getenv('BULLY_LISTEN_PORT', 9000)
    bully_peer_addrs = os.environ['BULLY_PEERS_INFO'].split(',')
    bully = BullyManager(node_id, bully_peer_addrs, bully_port)
    bully.start()

    vault_peers = [addr for addr in os.environ['VAULT_PEERS_INFO'].split(
        ',') if not addr.startswith(f"{node_id}-")]
    vault_port = os.environ['VAULT_LISTEN_PORT']
    vault_timeout = int(os.environ['VAULT_TIMEOUT'])
    event_con_start = THEvent()
    vault_cm = ConnectionsManager(
        node_id, vault_port, vault_peers, event_con_start, vault_timeout)

    logging.info("Waiting for initialization...")

    logging.info("Initialization finished!")

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

    def new_leader_callback():
        print("CALLBACK")

        if started[0]:
            if i_am_leader[0] and not bully.get_is_leader():
                logging.info(f'[NODE {node_id}] I was the leader. Now exiting')
                server.stop()
            elif not i_am_leader[0]:
                logging.info(f'[NODE {node_id}] I was follower. follower.stop()')
                vault.follower_stop()

        if not started[0]:
            # print("Before ACQ started_cv")
            started_cv.acquire()
            started[0] = True
            started_cv.notify_all()
            started_cv.release()

    bully.set_callback(Event.NEW_LEADER, new_leader_callback)

    started_cv.acquire()
    started_cv.wait_for(lambda: started[0])
    started_cv.release()

    exited = False
    while not exited:
        i_am_leader[0] = bully.get_is_leader()
        if i_am_leader[0]:
            logging.info(f"Leader Started")
            exited = leader_start(server)
            logging.info(f"Leader finished: {exited}")
        else:
            leader_addr = bully.get_leader_addr()
            logging.info(f"Follower Started with leader: {leader_addr}")
            exited = follower_start(vault, leader_addr)
            logging.info(f"Follower finished: {exited}")

    vault_cm.shutdown_connections()
    bully.shutdown_connections()

    bully.join()
    bully._join_listen_thread()
    vault_cm._join_listen_thread()
