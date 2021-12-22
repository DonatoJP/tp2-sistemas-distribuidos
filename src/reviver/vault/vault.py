import logging
from math import floor
from multiprocessing.pool import ThreadPool
from threading import Lock
import time

from connections_manager import ConnectionsManager
from connections_manager.conn_errors import RecvTimeout

from .storage import Storage
from .validate import validate_key, validate_value


logger = logging.getLogger("Vault")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s]-%(levelname)s-%(name)s-%(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)

class Vault:
    """Distributed, replicated, highly available kay-value store"""

    def __init__(self, cluster: ConnectionsManager, storage_path="/storage", buckets_number=20):
        self.cluster = cluster
        self.pool = ThreadPool(len(cluster.connections))
        self.storage = Storage(storage_path, buckets_number)
        self.follower_keep_listening = True
        self.follower_lock = Lock()
        self.cluster_quorum = floor((len(self.cluster.connections) + 1) / 2) + 1

    def set_leader_addr(self, leader_addr):
        with self.follower_lock:
            self.leader_addr = leader_addr

    def follower_listen(self):
        with self.follower_lock:
            self.follower_keep_listening = True

        logger.info("Waiting for messages from leader")
        while self.follower_keep_listening:
            # Solo se puede cambiar el leader cuando no hay una operacion siendo procesada
            with self.follower_lock:

                # Necesitamos un timeout para que cada tanto salga del recv_from y pueda cambiar de leader
                # logger.info("Waiting for new message from leader")
                try:
                    message = self.cluster.recv_from(self.leader_addr)
                except RecvTimeout:
                    continue
                if message is None:
                    if self.follower_keep_listening:
                        # logger.info("Follower continueing")
                        logger.info("Leader down")
                        break
                    else:
                        logger.info("Follower exiting")
                        break

                # logger.info(f"Got message {message} from leader")

                # Se podria optimizar esto con una pool de workers?
                op, params = message.split(" ", 1)
                if op == "GET":
                    res = self._follower_get(params)
                elif op == "POST":
                    version, rest = params.split(":", 1)
                    key, value = rest.split("=", 1)
                    res = self._follower_post(version, key, value)
                elif op == "VERSION":
                    res = self._follower_version(params)

                try:
                    self.cluster.send_to(self.leader_addr, res)
                except:
                    # Leader down, abort operation
                    pass

        logger.info("Follower quiting")

    def follower_stop(self):
        self.follower_keep_listening = False

    def _follower_get(self, key):
        res = self.storage.get(key)
        if res is None:
            return "0:"

        version, value = res
        return f"{version}:{value}"

    def _follower_post(self, version, key, value):
        self.storage.post(version, key, value)
        return "ACK"

    def _follower_version(self, key):
        return str(self.storage.version(key))

    def leader_get(self, key: str, last_responses=False) -> tuple:
        """
        gets from vault a value searching by the key
        returns (retry, value)

        if error is false and value is none, it means that the key was not found in the store
        """

        start = time.time()

        key = key.strip()
        validate_key(key)

        # logger.debug(f"VALIDATED KEYS: {time.time() - start}")

        self.cluster.clear_all_responses()

        # logger.debug(f"CLEARED RESPONSES: {time.time() - start}")

        message = f"GET {key}"
        self.cluster.send_to_all(message)

        # logger.debug(f"SENT GET TO FOLLOWERS: {time.time() - start}")

        responses = self._get_responses()

        # logger.debug(f"GOT RESPONSES FROM FOLLOWERS: {time.time() - start}")

        responses.append(self._follower_get(key))

        # logger.debug(f"GOT OWN RESPONSE: {time.time() - start}")

        if len(responses) < self.cluster_quorum:
            return True, None

        def parse_respone(res):
            try:
                version, value = res.split(':', 1)
            except ValueError:
                return 0, None

            return int(version), value

        parsed_responses = map(parse_respone, filter(
            lambda res: res is not None, responses))
        most_recent_value = max(parsed_responses, key=lambda res: res[0])

        if most_recent_value[0] == 0:
            return False, None

        # logger.debug(f"PROCESS RESPONSES: {time.time() - start}")

        return False, most_recent_value[1]

    def leader_post(self, key: str, value: str, last_responses=False) -> bool:
        """
        inserts a value by indexed by key on vault
        key must not contain "=" or newline characters
        value must not contain the newline character
        key will be striped

        returns True if client must retry
        """
        key = key.strip()
        validate_key(key)
        validate_value(key)

        logger.debug("Getting versions")

        self.cluster.clear_all_responses()

        message = f"VERSION {key}"
        self.cluster.send_to_all(message)
        responses = self._get_responses()
        responses.append(self._follower_version(key))

        if len(responses) < self.cluster_quorum:
            return True

        # print(f"Got responses: {responses}")

        def parse_response(res):
            try:
                return int(res)
            except ValueError:
                return 0

        parsed_responses = map(parse_response, filter(
            lambda res: res is not None, responses))
        next_version = max(parsed_responses) + 1

        logger.debug(f"Next version: {next_version}")
        logger.debug(f"Executing posts")

        message = f"POST {next_version}:{key}={value}"
        self.cluster.send_to_all(message)
        # Que get responses no espere a todos. Que pueda salir una vez que ya tiene quorum
        responses = self._get_responses()
        responses.append(self._follower_post(next_version, key, value))

        logger.debug(f"Got responses: {responses}")

        return responses.count("ACK") < self.cluster_quorum

    def _get_responses(self):
        def recv (peer_addr):
            for i in range(5):
                try:
                    return self.cluster.recv_from(peer_addr)
                except RecvTimeout:
                    pass

            return None

        return self.pool.map(recv, self.cluster.addresses)
