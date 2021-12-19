import os, logging, threading

from bully import BullyManager
from coordinator.state import State
from coordinator.server import UdpServer
from coordinator.reviver import Reviver
from heartbeat.heartbeat import Heartbeat


state = State()

# format = "%(asctime)s: %(message)s"
# reduce log level
logging.getLogger("pika").setLevel(logging.WARNING)
logging.basicConfig(format="[%(asctime)s]-%(levelname)s-%(name)s-%(message)s", level=logging.INFO, datefmt="%H:%M:%S")


def main():
    # or, disable propagation
    logging.getLogger("pika").propagate = False
    threads = []

    event = threading.Event()
    heartbeat_t = Heartbeat(event)
    heartbeat_t.start()
    threads.append(heartbeat_t)

    udp_server = UdpServer(state)  # threading.Thread(target=server.run, args=(state,))
    udp_server.start()
    threads.append(udp_server)

    node_id = os.getenv('NODE_ID', 1)
    bully_port = os.getenv('BULLY_LISTEN_PORT', 9000)
    bully_peer_addrs = os.environ['BULLY_PEERS_INFO'].split(',')
    print("node_id", node_id)
    print("bully_port", bully_port)
    print("bully_peer_addrs", bully_peer_addrs)
    bully = BullyManager(node_id, bully_peer_addrs, bully_port)
    # logging.info("Sleeping root")
    # time.sleep(3)
    bully.start()


    state_checker = Reviver(state, bully)
    state_checker.start()
    threads.append(state_checker)

    # [t.join() for t in threads]
    bully._join_listen_thread()
    bully.join()
    # event.set()


if __name__ == "__main__":
    main()
