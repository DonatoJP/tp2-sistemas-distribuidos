from abc import ABC, abstractmethod
from functools import reduce
from reviver.state_saver import Storable

class AbstractHolder(Storable):
    name = 'AbstractHolder'

    def export_state(self):
        ret = {}
        ret["perform_affinity"] = self.perform_affinity
        ret["affinity_key"] = self.affinity_key
        ret["affinity_divider"] = self.affinity_divider
        return ret

    def __str__(self) -> str:
        return f'{self.name} {self.export_state()}'

    def __init__(self, perform_affinity, affinity_key='', affinity_divider=1) -> None:
        self.perform_affinity = perform_affinity
        self.affinity_key = affinity_key
        self.affinity_divider = affinity_divider
        super().__init__(self.name)
    
    def _get_affinity(self, msg_to_send: dict):
        if not msg_to_send[self.affinity_key]:
            return ''

        return int(float(msg_to_send[self.affinity_key]) % self.affinity_divider)

    def get_affinity(self, msg_to_send: dict):
        return '' if (not self.perform_affinity) else self._get_affinity(msg_to_send)
    
    @staticmethod
    def _group_by_ak(data):
        def reduce_by_ak(acc, value):
            if value[1] in acc:
                acc[value[1]].append(value[0])
            else:
                acc[value[1]] = [ value[0] ]
            return acc

        res = reduce(reduce_by_ak, data, {})
        return [ (x[1], x[0]) for x in res.items() ]
    
    @abstractmethod
    def exec_operation(self, data, **kwargs) -> list:
        pass

    @abstractmethod
    def end(self):
        pass