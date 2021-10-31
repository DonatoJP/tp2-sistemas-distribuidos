from abc import ABC, abstractmethod

class AbstractHolder:
    def __init__(self, perform_affinity, affinity_key='', affinity_divider=1) -> None:
        self.perform_affinity = perform_affinity
        self.affinity_key = affinity_key
        self.affinity_divider = affinity_divider
        super().__init__()
    
    def _get_affinity(self, msg_to_send: dict):
        return int(msg_to_send[self.affinity_key]) % self.affinity_divider

    def get_affinity(self, msg_to_send: dict):
        return '' if (not self.perform_affinity) else self._get_affinity(msg_to_send)
    
    def get_affinity_posible_values(self) -> list:
        return [] if (not self.perform_affinity) else [str(x) for x in range(0, self.affinity_divider)]
    
    @abstractmethod
    def exec_operation(self, data, **kwargs) -> list:
        pass

    @abstractmethod
    def end(self):
        pass