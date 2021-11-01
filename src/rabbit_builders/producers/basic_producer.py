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
    
    def _send_centinel_by_pattern(self, centinel):
        for rk in range(0, self.centinels_to_send):
            if self.pattern == 'work_queue':
                print(f"[CENTINEL] Sending {centinel} to exchange {self.exchange_name} and routing key {self.queue_name}")
                self.send(centinel)
            else:
                print(f"[CENTINEL] Sending {centinel} to exchange {self.exchange_name} and routing key {str(rk)}")
                self.send(centinel, str(rk))
    
    def _send_centinel_by_routing_keys(self, centinel, routing_keys):
        for _ in range(0, self.centinels_to_send):
            for rk in routing_keys:
                self.send(centinel, str(rk))

    def send_end_centinels(self, centinel, routing_keys=[]):
        if len(routing_keys) > 0:
            self._send_centinel_by_routing_keys(centinel, routing_keys)
        else:
            self._send_centinel_by_pattern(centinel)
    
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