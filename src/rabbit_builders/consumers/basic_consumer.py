import pika
from ..abstract_builder import AbstractQueueHandler

class QueueConsumer(AbstractQueueHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def init_queue_pattern(self, pattern, callback, queue_name='', auto_ack=False):
        self.queue_name = queue_name
        self.queue = self.channel.queue_declare(queue=queue_name, durable=False)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)
    
    def start_consuming(self):
        self.channel.start_consuming()
    
    def close(self):
        super().close()