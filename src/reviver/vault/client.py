import pika
import pickle, logging
from threading import Lock
from log import create_logger
logger = create_logger(__name__)

from .validate import validate_key, validate_value

class VaultClient:
    def __init__(self, rabbit_addr, input_queue_name):
        self.rabbit_lock = Lock()

        connection_parameters = pika.ConnectionParameters(rabbit_addr)
        connection = pika.BlockingConnection(connection_parameters)

        self.channel = connection.channel()

        self.input_queue_name = input_queue_name
        self.channel.queue_declare(input_queue_name)

        res = self.channel.queue_declare("")
        self.res_queue_name = res.method.queue
        logger.info("Vault Client Init")


    def get(self, key):
        with self.rabbit_lock:
            validate_key(key)

            message = f"GET {self.res_queue_name} {key}"
            logger.debug("Publishing GET message")
            self.channel.basic_publish("", self.input_queue_name, message)

            logger.debug("Waiting on consume message")
            method_frame, properties, body = next(self.channel.consume(
                self.res_queue_name, auto_ack=True))

            logger.debug("Got Message len %s", len(body))
            ret = ""
            if len(body) == 0:
                return ret
            try:
                ret = pickle.loads(bytes.fromhex(body.decode()))
            except Exception as e:
                logger.warning("Exception %s: cant decode body %s with %s", e, body, body.decode())

            return ret

    def post(self, key: str, value):
        with self.rabbit_lock:
            validate_key(key)

            value = pickle.dumps(value).hex()
            message = f"POST {key}={value}"
            logger.debug("Publishing POST message")

            self.channel.basic_publish("", self.input_queue_name, message)

            logger.debug("Sent POST KEY Message len %s", len(message))

    def post_key(self, key1: str, key2: str, value):
        with self.rabbit_lock:
            validate_key(key1)
            validate_key(key2)

            value = pickle.dumps(value).hex()
            message = f"POST_KEY {key1}={key2}={value}"

            logger.debug("Publishing POST KEY message")

            self.channel.basic_publish("", self.input_queue_name, message)
            
            logger.debug("Sent POST KEY Message len %s", len(message))

    def get_key(self, key1: str, key2: str):
        with self.rabbit_lock:
            validate_key(key1)
            validate_key(key2)

            message = f"GET_KEY {self.res_queue_name} {key1}={key2}"
            self.channel.basic_publish("", self.input_queue_name, message)

            method_frame, properties, body = next(self.channel.consume(
                self.res_queue_name, auto_ack=True))

            if len(body) == 0:
                return ""

            return pickle.loads(bytes.fromhex(body.decode()))

    def get_all(self, key1) -> dict:
        user_dict: dict = self.get(key1)

        res = dict()

        for key, value in user_dict.items():
            res[key] = pickle.loads(bytes.fromhex(value))

        return res
