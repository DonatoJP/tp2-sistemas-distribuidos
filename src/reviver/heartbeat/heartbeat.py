from threading import Thread
import threading
import time
from socket import *
import json
import os
import random
from log import create_logger
logger = create_logger(__name__)


HOSTNAME = os.getenv("HOSTNAME", "tp3_heartbeat")
COORDINATOR_HOSTNAME = os.getenv("COORDINATOR_HOSTNAME", "coordinator")
COORDINATOR_PORT = int(os.getenv("COORDINATOR_PORT", 12000))
COORDINATOR_AMOUNT = int(os.getenv("COORDINATOR_AMOUNT", 1))
HEARTBEAT_TIME = 5


class Heartbeat(Thread):
    def __init__(self, event: threading.Event):
        # Call the Thread class's init function
        Thread.__init__(self)
        self.__event = event

    def run(self):
        pings = 0
        logger.info(f"Created {HOSTNAME}")
        while not self.__event.is_set():
            idx = random.randint(1, COORDINATOR_AMOUNT)
            clientSocket = socket(AF_INET, SOCK_DGRAM)
            coordinator_host = f"{COORDINATOR_HOSTNAME}{idx}"
            message = {"host": HOSTNAME, "message": "ping"}
            addr = (coordinator_host, COORDINATOR_PORT)
            logger.debug("Sending status to %s", coordinator_host)
            try:
                res = clientSocket.sendto(
                    bytes(json.dumps(message), encoding="utf-8"), addr
                )
                # logger.info("res %s", res)
                pings += 1
                logger.info("PINGS COUNT %s", pings)
                time.sleep(HEARTBEAT_TIME)
            except Exception:
                logger.debug(f"Coordinator <{idx}> unrechable, next random?")
