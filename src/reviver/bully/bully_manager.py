import logging
from threading import Condition, Lock, Thread
from time import sleep
from bully.events_enum import Event
from connections_manager import ConnectionsManager
from . import Bully
import os, time

class BullyManager(Thread):
    def __init__(self, node_id, peer_hostnames, port_n, new_leader_callback=None):
        Thread.__init__(self)
        self.node_id = node_id
        self.peer_hostnames = peer_hostnames
        self.port_n = int(port_n)
        self.bully = None
        self.bully_cv = Condition(Lock())
        self.new_leader_callback = new_leader_callback

    def run(self) -> None:
        bully_port = self.port_n
        bully_cm = ConnectionsManager(self.node_id, bully_port, self.peer_hostnames)
        pre_bully_peers = list(filter(lambda x: not x.startswith(f'{self.node_id}-'), self.peer_hostnames))
        bully_peers = list(map(lambda x: x.split(':')[0].split('-')[1], pre_bully_peers))

        logging.info(f"BULLY PEERS: {bully_peers}")

        # logging.info("SLEEPING... ")
        # time.sleep(5)

        self.bully_cv.acquire()
        logging.info("Starting Bully")
        self.bully = Bully(bully_cm, bully_peers, self.new_leader_callback)
        logging.info("Bully finished")
        self.bully_cv.notify_all()
        self.bully_cv.release()

        self.bully.begin_election_process()

        # self.bully.conn_manager._join_listen_thread()
        return super().run()

    def _wait_until_bully_is_ready(self):
        self.bully_cv.acquire()
        self.bully_cv.wait_for(lambda: self.bully)
        self.bully_cv.release()

    def set_callback(self, event: Event, callback) -> None:
        self._wait_until_bully_is_ready()
        self.bully.set_callback(event, callback)

    def shutdown_connections(self):
        self._wait_until_bully_is_ready()
        self.bully.conn_manager.shutdown_connections()

    def _join_listen_thread(self):
        self._wait_until_bully_is_ready()
        self.bully.conn_manager._join_listen_thread()

    def begin_election_process(self):
        self._wait_until_bully_is_ready()
        self.bully.begin_election_process()

    def get_is_leader(self):
        self._wait_until_bully_is_ready()
        return self.bully.get_is_leader()

    def get_leader_addr(self):
        self._wait_until_bully_is_ready()
        return self.bully.get_leader_addr()
