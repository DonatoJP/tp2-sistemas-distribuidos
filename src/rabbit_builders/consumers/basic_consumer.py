import pika
from ..abstract_builder import AbstractQueueHandler

class QueueConsumer(AbstractQueueHandler):

    def _build_work_queue_pattern(self, queue_name, callback, auto_ack=False):
        super()._build_work_queue_pattern(queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)

    def _build_direct_pattern(self, exchange_name, callback, routing_key, auto_ack=False):
        super()._build_direct_pattern(exchange_name)

        result = self.channel.queue_declare(queue='')
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=self.queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=auto_ack)

    def __init__(self) -> None:
        super().__init__()
    
    def init_queue_pattern(self, pattern, **kwargs):
        super().init_queue_pattern(pattern, **kwargs)

    def start_consuming(self):
        self.channel.start_consuming()
    
    def close(self):
        super().close()