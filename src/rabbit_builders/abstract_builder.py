from abc import ABC, abstractmethod
import pika

class AbstractQueueHandler:
    def _build_work_queue_pattern(self, queue_name):
        self.queue_name = queue_name
        self.queue = self.channel.queue_declare(queue=queue_name)
    
    def _build_direct_pattern(self, exchange_name):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        self.exchange_name = exchange_name

    def init_queue_pattern(self, pattern, **kwargs):
        if pattern not in self.patterns.keys():
            raise Exception(f'Pattern {pattern} not implemented')
        
        self.pattern = pattern
        self.patterns[pattern](**kwargs)

    def __init__(self) -> None:
        host = 'rabbitmq-tp2'
        port = '5672'
        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        self.channel = self.connection.channel()
        self.queue = None
        self.exchange_name = ''
        self.queue_name = ''
        self.pattern = ''

        self.patterns = { "work_queue": self._build_work_queue_pattern, "direct": self._build_direct_pattern }
        super().__init__()

    def close(self):
        self.channel.close()