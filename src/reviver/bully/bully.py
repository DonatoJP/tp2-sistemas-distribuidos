from typing import Callable
from connections_manager import ConnectionsManager
from .events_enum import Event
from threading import Thread, Condition, Lock, Event as THEvent
import time
from log import create_logger
logger = create_logger(__name__)

# logger = logging.getLogger("Bully")
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter("[%(asctime)s]-%(levelname)s-%(name)s-%(message)s")
# sh = logging.StreamHandler()
# sh.setFormatter(formatter)
# logger.addHandler(sh)


class Bully:
    def __init__(self,
                 connection_manager: ConnectionsManager,
                 peer_hostnames: "list[str]",
                 new_leader_callback=None
                 ) -> None:
        self.conn_manager = connection_manager
        self.peer_hostnames = peer_hostnames
        self.threads = []
        self.callbacks = {}
        self.is_in_election = False
        self.is_in_election_cv = Condition(Lock())
        self.ready_peers = 0
        self.bully_is_ready = False
        self.bully_is_ready_cv = Condition(Lock())

        self.received_ok = False
        self.received_ok_cv = Condition(Lock())

        self.received_ping_echo = False
        self.received_ping_echo_cv = Condition(Lock())

        self.leader_addr = None
        self.leader_addr_cv = Condition(Lock())

        self.is_leader = False
        self.is_leader_cv = Condition(Lock())

        self.new_leader_callback = new_leader_callback

        for ph in peer_hostnames:
            th = Thread(target=self._start_receiving_from_peer, args=(ph,))
            th.daemon = True
            th.start()
            self.threads.append(th)

        ping_thread = Thread(target=self._poll_leader)
        ping_thread.daemon = True
        ping_thread.start()
        self.threads.append(ping_thread)

        logger.info("Waiting for all connections")

        self._wait_until_all_are_ready()

        logger.info("All peers connected")

    def wait_bully_ready(self):
        self.bully_is_ready_cv.acquire()
        self.bully_is_ready_cv.wait_for(lambda: self.bully_is_ready)
        self.bully_is_ready_cv.release()

    def _wait_until_all_are_ready(self):
        self.conn_manager.send_to_all('READY')

        self.wait_bully_ready()

    def _poll_leader(self):
        """
            Private function. If the node is not the leader, it sends PING messages expecting to receive
            an answer. If not, the node begins with the election process.
        """
        while True:
            self.is_leader_cv.acquire()
            self.is_in_election_cv.acquire()
            self.leader_addr_cv.acquire()

            if not self.is_leader and not self.is_in_election and self.leader_addr is not None:
                self.is_in_election_cv.release()
                self.is_leader_cv.release()

                logger.debug(f"Sending PING to {self.leader_addr}")

                self.conn_manager.send_to(self.leader_addr, 'PING')
                self.leader_addr_cv.release()

                received_ping_echo = self.wait_get_received_ping_echo(7)
                if not received_ping_echo:
                    logger.info(
                        f'I detect that LEADER is down. Beggining with election process...')
                    self.begin_election_process()
            else:
                self.is_leader_cv.release()
                self.is_in_election_cv.release()
                self.leader_addr_cv.release()

            self.set_received_ping_echo(False)
            time.sleep(15)

    def get_is_leader(self):
        """
            Returns boolean indicating if this node is the leader in the cluster.
        """
        self.is_leader_cv.acquire()
        is_leader = self.is_leader
        self.is_leader_cv.release()
        return is_leader

    def set_is_leader(self, value):
        self.is_leader_cv.acquire()
        self.is_leader = value
        self.is_leader_cv.release()

    def get_leader_addr(self):
        """
            Returns the address of the leader.
        """
        self.leader_addr_cv.acquire()
        leader_addr = self.leader_addr
        self.leader_addr_cv.release()
        return leader_addr

    def set_leader_addr(self, value):
        self.leader_addr_cv.acquire()
        self.leader_addr = value
        self.leader_addr_cv.release()

    def get_is_in_election(self):
        self.is_in_election_cv.acquire()
        is_in_election = self.is_in_election
        self.is_in_election_cv.release()
        return is_in_election

    def set_is_in_election(self, value):
        self.is_in_election_cv.acquire()
        self.is_in_election = value
        self.is_in_election_cv.release()

    def get_received_ok(self):
        self.received_ok_cv.acquire()
        received_ok = self.received_ok
        self.received_ok_cv.release()
        return received_ok

    def wait_get_received_ok(self, timeout):
        """
            Executes wait on received_ok condvar for 'timeout' seconds. Then, it returns the value of
            received_ok
        """
        self.received_ok_cv.acquire()
        self.received_ok_cv.wait(timeout)
        received_ok = self.received_ok
        self.received_ok_cv.release()
        return received_ok

    def set_received_ok(self, value):
        self.received_ok_cv.acquire()
        self.received_ok = value
        self.received_ok_cv.release()

    def notify_set_received_ok(self, value):
        """
            Set a new value for received_ok and notifies all threads waiting for a change on it.
        """
        self.received_ok_cv.acquire()
        self.received_ok = value
        self.received_ok_cv.notify_all()
        self.received_ok_cv.release()

    def wait_get_received_ping_echo(self, timeout):
        """
            Executes wait on received_ping_echo condvar for 'timeout' seconds. Then, it returns the value of
            received_ping_echo
        """
        self.received_ping_echo_cv.acquire()
        self.received_ping_echo_cv.wait(timeout)
        received_ping_echo = self.received_ping_echo
        self.received_ping_echo_cv.release()
        return received_ping_echo

    def notify_set_received_ping_echo(self, value):
        """
            Set a new value for received_ping_echo and notifies all threads waiting for a change on it.
        """
        self.received_ping_echo_cv.acquire()
        self.received_ping_echo = value
        self.received_ping_echo_cv.notify_all()
        self.received_ping_echo_cv.release()

    def get_received_ping_echo(self):
        self.received_ping_echo_cv.acquire()
        received_ping_echo = self.received_ping_echo
        self.received_ping_echo_cv.release()
        return received_ping_echo

    def set_received_ping_echo(self, value):
        self.received_ping_echo_cv.acquire()
        self.received_ping_echo = value
        self.received_ping_echo_cv.release()

    def begin_election_process(self):
        """
            Begins with the leader election process. It may execute the ELECTION_STARTED callback,
            if it is set
        """
        if self.get_is_in_election():
            return
        self.set_is_in_election(True)

        if Event.ELECTION_STARTED in self.callbacks:
            self.callbacks[Event.ELECTION_STARTED]()

        self.conn_manager.send_to_higher('ELECTION')
        received_ok = self.wait_get_received_ok(5)  # TODO: Timeout as env var

        if not received_ok:
            self._proclaim_leader()

    def _proclaim_leader(self):
        """
            Private function. Proclaims the node as the leader in the cluster.
        """
        logger.info('I am the new LEADER !')
        self.conn_manager.send_to_all('LEADER')
        self.set_is_leader(True)
        self.set_leader_addr(None)

        self._reset_election_variables()

        logger.info("Calling callback 1")

        if Event.NEW_LEADER in self.callbacks:
            logger.info("Calling callback 2")
            self.callbacks[Event.NEW_LEADER](self)

        if self.new_leader_callback:
            logger.info("Calling callback 3")
            self.new_leader_callback(self)

    def _process_election_message(self, peer_addr):
        """
            Process message of type ELECTION. It sends "Ok" to the sender and starts new election process
        """
        logger.info(f'Received ELECTION message from {peer_addr}')

        # Responder con OK y comenzar proceso de eleccion
        self.conn_manager.send_to(peer_addr, 'OK')
        self.begin_election_process()

    def _process_ok_message(self, peer_addr):
        """
            Process message of type OK. It notify the reception of the OK message to other threads
        """
        logger.info(f'Received OK message from {peer_addr}')
        self.notify_set_received_ok(True)

    def _process_leader_message(self, peer_addr):
        """
            Process message of type LEADER. Configures new leader address. Executes callback NEW_LEADER, if set.
        """
        logger.info(f'Received LEADER message from {peer_addr}')
        self.set_leader_addr(peer_addr)
        self.set_is_leader(False)

        logger.info(f'My new LEADER is now {peer_addr} !!')
        self._reset_election_variables()

        if Event.NEW_LEADER in self.callbacks:
            self.callbacks[Event.NEW_LEADER](self)

        if self.new_leader_callback:
            logger.info("Calling callback 3")
            self.new_leader_callback(self)

    def _reset_election_variables(self):
        self.set_is_in_election(False)
        self.set_received_ok(False)

    def _echo_ping(self, peer_addr):
        """
            Process message of type PING. Answers with ECHO_PING
        """

        self.conn_manager.send_to(peer_addr, 'ECHO_PING')
        logger.debug(f"Sent ECHO_PING to {peer_addr}")

    def _start_receiving_from_peer(self, peer_addr):
        logger.info(f'Starting to receive from {peer_addr}')
        while True:
            try:
                msg = self.conn_manager.recv_from(peer_addr)
            except Exception as e:
                logger.info(e)
                continue

            if msg is None:
                logger.info(f'Waiting until {peer_addr} is back again')
                self.conn_manager.wait_until_back_again(peer_addr)
                logger.info(
                    f'{peer_addr} is back again. The show must go on!')
                self.conn_manager.send_to(peer_addr, "READY")
                continue
            elif msg == 'ELECTION':
                self._process_election_message(peer_addr)
            elif msg == 'OK':
                self._process_ok_message(peer_addr)
            elif msg == 'LEADER':
                self._process_leader_message(peer_addr)
            elif msg == 'PING':
                logger.debug(f"Received PING from {peer_addr}")
                self._echo_ping(peer_addr)
            elif msg == 'ECHO_PING':
                logger.debug(f"Received ECHO PING from {peer_addr}")
                self.notify_set_received_ping_echo(True)
            elif msg == 'READY':
                logger.info(f"Got READY message from {peer_addr}")
                self._process_ready_message(peer_addr)
            elif msg == 'ECHO_READY':
                logger.info(f"Got ECHO_READY message from {peer_addr}")
                self._process_echo_ready_message()

    def _process_ready_message(self, peer_addr):
        logger.info("Processing READY message")
        self.bully_is_ready_cv.acquire()
        logger.info(f"Got is ready lock: {self.bully_is_ready}")
        if self.bully_is_ready:
            self.conn_manager.send_to(peer_addr, 'ECHO_READY')
            self.bully_is_ready_cv.release()
        else:
            self.ready_peers += 1
            if self.ready_peers == len(self.conn_manager.connections):
                self.bully_is_ready = True
                self.bully_is_ready_cv.notify_all()
            self.bully_is_ready_cv.release()

    def _process_echo_ready_message(self):
        self.bully_is_ready_cv.acquire()
        self.bully_is_ready = True
        self.bully_is_ready_cv.notify_all()
        self.bully_is_ready_cv.release()

    def set_callback(self, event: Event, callback: Callable):
        """
            Configures callback on event. Event must be type Event from events_enum:

            Event.NEW_LEADER
            Event.ELECTION_STARTED
            Event.LEADER_DOWN
        """
        self.callbacks[event] = callback
