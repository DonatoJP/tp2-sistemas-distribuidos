import pika
from ..abstract_builder import AbstractQueueHandler

class QueueProducer(AbstractQueueHandler):
    def __init__(self, next_step_count) -> None:
        self.next_step_count = next_step_count
        super().__init__()

    def _build_work_queue_pattern(self, queue_name):
        super()._build_work_queue_pattern(queue_name)

    def init_queue_pattern(self, pattern, **kwargs):
        super().init_queue_pattern(pattern, **kwargs)
    
    def send_end_centinels(self, centinel):
        for _ in range(0, self.next_step_count):
            self.send(centinel)
    
    def send(self, message):
        self.channel.basic_publish(exchange='',
            routing_key=self.queue_name,
            body=message)
    
    def close(self):
        super().close()