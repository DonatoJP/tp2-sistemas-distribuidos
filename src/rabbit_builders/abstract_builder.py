from abc import ABC, abstractmethod
import pika

class AbstractQueueHandler:
    def __init__(self) -> None:
        host = 'rabbitmq-tp2'
        port = '5672'
        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        self.channel = self.connection.channel()
        self.queue = None
        self.queue_name = None

        super().__init__()
    
    @abstractmethod
    def init_queue_pattern(self, pattern, queue_name='', auto_ack=False):
        pass

    def close(self):
        self.channel.close()