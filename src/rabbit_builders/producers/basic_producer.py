import pika
from ..abstract_builder import AbstractQueueHandler

class QueueProducer(AbstractQueueHandler):
    def __init__(self, next_step_count) -> None:
        self.next_step_count = next_step_count
        super().__init__()

    def init_queue_pattern(self, pattern, queue_name='', auto_ack=False):
        self.queue_name = queue_name
        self.channel.queue_declare(queue=queue_name)
    
    def send_end_centinels(self, centinel):
        for _ in range(0, self.next_step_count):
            self.send(centinel)
    
    def send(self, message):
        self.channel.basic_publish(exchange='',
            routing_key=self.queue_name,
            body=message)
    
    def close(self):
        super().close()