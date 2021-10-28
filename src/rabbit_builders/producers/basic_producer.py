import pika
from ..abstract_builder import AbstractQueueHandler

class QueueProducer(AbstractQueueHandler):
    def __init__(self) -> None:
        super().__init__()

    def init_queue_pattern(self, pattern, queue_name='', auto_ack=False):
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name, durable=True)
    
    def send_end_centinel(self):
        self.channel.basic_publish(exchange='', 
            routing_key=self.queue_name,
            body='END')
    
    def send(self, message):
        self.channel.basic_publish(exchange='',
            routing_key=self.queue_name,
            body=message)
    
    def close(self):
        super().close()