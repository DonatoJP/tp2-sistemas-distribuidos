from abc import ABC, abstractmethod

class AbstractOperator:
    def __init__(self, perform_affinity=False, affinity_key='', affinity_divider=1) -> None:
        self.perform_affinity = perform_affinity
        self.affinity_key = affinity_key
        self.affinity_divider = affinity_divider
        super().__init__()
    
    def _get_affinity(self, msg_to_send: dict):
        if not msg_to_send[self.affinity_key]:
            return ''

        return int(float(msg_to_send[self.affinity_key]) % self.affinity_divider)

    def get_affinity(self, msg_to_send: dict):
        return '' if (not self.perform_affinity) else self._get_affinity(msg_to_send)
    
    def get_all_routing_keys(self):
        return []
    
    @abstractmethod
    def exec_operation(self, data, **kwargs) -> list:
        pass