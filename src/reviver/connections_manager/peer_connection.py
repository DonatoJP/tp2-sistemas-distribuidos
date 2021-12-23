import socket
import select
import logging
from .conn_errors import ConnectionClosed, RecvTimeout
from threading import Condition, Lock
from log import create_logger
logger = create_logger(__name__)


class PeerConnection:
    def __init__(self, addr, port, node_id, timeout=None) -> None:
        self.peer_addr = addr
        self.peer_port = int(port)
        self.node_id = int(node_id)
        self.timeout = timeout

        self.peer_conn = None
        self.peer_conn_cv = Condition(Lock())

        self.is_up = True
        self.is_up_cv = Condition(Lock())

    def _is_ip(self, ip):
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False

        return True

    def is_peer(self, peer_addr):
        if self._is_ip(peer_addr):
            hostname = socket.gethostbyaddr(peer_addr)[0].split('.')[0]
            logger.info("is ip!")
        else:
            hostname = peer_addr.split(":")[0]
        return self.peer_addr == hostname

    def is_higher(self, peer_id: int):
        return self.node_id > peer_id

    def set_connection(self, conn: socket.socket):
        self.peer_conn_cv.acquire()

        # Closing latest connection
        if self.peer_conn is not None:
            self.peer_conn.close()

        self.peer_conn = conn
        logger.info(f'Setting new connection: {conn}')
        self.peer_conn_cv.notify_all()
        self.peer_conn_cv.release()

        self.is_up_cv.acquire()
        self.is_up = True
        self.is_up_cv.notify_all()
        self.is_up_cv.release()

    def shutdown(self):
        if self.peer_conn:
            self.peer_conn.close()

    def init_connection(self):
        # Already stablished connection
        if self.peer_conn is not None:
            return

        logger.info(f"Connecting to {self.peer_addr}")

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_host = (self.peer_addr, self.peer_port)
        try:
            conn.connect(peer_host)
            self.set_connection(conn)
            logger.info(
                f'[Main Thread] Connection to {peer_host} successfully done!')
        except ConnectionRefusedError as e:
            logger.info(
                f'[Main Thread] Could not connect to {peer_host}. It is not yet active...')
        except Exception as e:
            logger.warning(
                f'Exception connecting to {peer_host}')

    def recv_message(self):

        # Receive first 4 bytes (len of message)
        try:
            msg_len = self._recv(4)

            # Receive Final Message
            msg = self._recv(int.from_bytes(msg_len, byteorder='big'))
        except ConnectionClosed as e:
            logger.debug("CONNECTION CLOSED")
            return None
        except ConnectionResetError:
            logger.debug("CONNECTION RESET")
            return None


        return msg.decode('utf-8')

    def perr_conn_is_valid(self):
        return self.peer_conn is not None and self.peer_conn.fileno() != -1

    def send_message(self, msg: str):
        logger.debug("Starting send message")

        if self.peer_conn is None:
            raise Exception("No hay socket")

        msg_bytes = bytes(msg, 'utf-8')
        msg_len = len(msg_bytes)
        to_send = msg_len.to_bytes(4, byteorder='big') + msg_bytes
        logger.debug("Sending to all! len %s", msg_len)
        logging.debug("Sending send.. %s, %s", len(to_send), to_send)

        if select.select([], [self.peer_conn], [], 0)[1]:
            try:
                self.peer_conn.sendall(to_send)
            except Exception as e:
                logging.warning(e)
                logging.warning("UNKOWN ERROR IN SEND ALL")
        else:
            logging.warning("Could not write to socket")

    def clear_responses(self):
        logger.debug("CLEARING RESPONSES")
        while select.select([self.peer_conn], [], [], 0)[0]:
            logger.debug("WE HAVE SOME MESSAGES")
            res = self.peer_conn.recv(1024)
            if len(res) == 0:
                logger.debug("BUT THEY WHERE EMPTY")
                break

        logger.debug("NO MORE MESSAGES IN SOCKET")


    def is_connected(self):
        return self.peer_conn != None

    def _recv(self, to_receive: int) -> bytes:
        result = b''
        received = b''
        aux = b''
        bytes_read = 0
        while True:
            ready = select.select([self.peer_conn], [], [], self.timeout)
            if ready[0]:
                aux += self.peer_conn.recv(to_receive - bytes_read)
                if not aux:
                    self.is_up_cv.acquire()
                    self.is_up = False
                    self.is_up_cv.release()
                    raise ConnectionClosed()
                received += aux
                aux = b''
                bytes_read += len(received)
                result += received
                if bytes_read >= to_receive:
                    break
            else:
                raise RecvTimeout("Receive Timeout")

        return result

    def _wait_until_back_again(self):
        self.is_up_cv.acquire()
        self.is_up_cv.wait_for(lambda: self.is_up)
        self.is_up_cv.release()

        return True
