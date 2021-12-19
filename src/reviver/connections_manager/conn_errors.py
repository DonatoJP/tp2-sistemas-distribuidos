class PeerDownError(Exception):
    """Raised when trying to use a Socket that belongs to a closed connection"""
    pass

class ConnectionClosed(Exception):
    """Raised when trying to read data from a connection that is closed"""
    pass

class RecvTimeout(Exception):
    """Raised when a timeout occurs while receiving from socket"""
    pass
