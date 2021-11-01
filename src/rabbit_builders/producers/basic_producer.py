import pika
from ..abstract_builder import AbstractQueueHandler

class QueueProducer(AbstractQueueHandler):
    def __init__(self, centinels_to_send) -> None:
        self.centinels_to_send = centinels_to_send
        super().__init__()

    def _build_work_queue_pattern(self, queue_name):
        super()._build_work_queue_pattern(queue_name)
    
    def _build_direct_pattern(self, exchange_name):
        super()._build_direct_pattern(exchange_name)

    def _build_topic_pattern(self, exchange_name):
        super()._build_topic_pattern(exchange_name)

    def init_queue_pattern(self, pattern, **kwargs):
        super().init_queue_pattern(pattern, **kwargs)
    
    def send_end_centinels(self, centinel):
        for rk in range(0, self.centinels_to_send):
            if self.pattern == 'work_queue':
                self.send(centinel)
            else:
                print(f"Sending centinel {centinel} to {rk}")
                self.send(centinel, str(rk))
    
    def send(self, message, routing_key=''):
        if routing_key == '':
            self.channel.basic_publish(exchange=self.exchange_name,
                routing_key=self.queue_name,
                body=message)
        else:
            self.channel.basic_publish(exchange=self.exchange_name,
                routing_key=str(routing_key),
                body=message)

    
    def close(self):
        super().close()