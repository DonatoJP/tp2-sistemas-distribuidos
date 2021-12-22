import docker
import time
from datetime import datetime
import logging
from threading import Thread, Timer
import time

from bully import BullyManager

from .state import State

STATE_CHECK_TIME = 5
CHECK_TIME_DIFF = 15
STATUS_RESTART = "restart"
STATUS_INVALID_KEY = "invalid_key"

# logging.basicConfig(level=logging.WARNING, datefmt="%H:%M:%S")
logger = logging.getLogger("Reviver")

class Reviver(Thread):
    def __init__(self, state: State, bully: BullyManager):
        # Call the Thread class's init function
        Thread.__init__(self)
        self.state = state
        self.bully = bully

    def thread_function(name):
        logger.info("Thread %s: starting", name)
        time.sleep(2)
        logger.info("Thread %s: finishing", name)

    def check_key_value(self, key, value, now):
        diff = (now - value).total_seconds()
        logger.info("Key %s, Diff %s", key, diff)
        if diff > CHECK_TIME_DIFF:
            logger.info("Client %s Down, restarting!", key)
            try:
                c = self.client.containers.get(key)
                c.restart()
                return {"key": key, "status": STATUS_RESTART}
            except Exception:
                return {"key": key, "status": STATUS_INVALID_KEY}

    def check_state(self):
        logger.info("Checking Leadership...")

        if self.bully.get_is_leader():
            logger.info("Is Leader!")
            now = datetime.now()

            hosts_to_revive = self.state.get_a("coordinator")
            logging.info(hosts_to_revive)

            res = [
                self.check_key_value(key, value, now)
                for key, value in hosts_to_revive.items()
                if value != ""
            ]
            # logging.WARNING("RES: %s", res)
            [
                self.state.remove_k("coordinator", r["key"])
                for r in res
                if r is not None and r["status"] == STATUS_INVALID_KEY
            ]
            now = datetime.now()
            [
                self.state.set_k("coordinator", r["key"], now)
                for r in res
                if r is not None and r["status"] == STATUS_RESTART
            ]
        else:
            logger.info("Not Leader, skipping!")

    def run(self):

        self.client = docker.from_env()
        while True:
            self.check_state()
            time.sleep(STATE_CHECK_TIME)
