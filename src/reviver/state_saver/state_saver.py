from reviver.vault.client import VaultClient
from .storable import Storable

class StateSaver():
    def __init__(self, mb_addr, input_queue_name) -> None:
        self.client = VaultClient(mb_addr, input_queue_name)

    def save_state(self, node_name, list_storables):
        to_save = {}
        for storable in list_storables:
            to_save[storable.name] = storable.export_state()

        self.client.post(node_name, to_save)

    def retrieve_state(self, node_name):
        state_retrieved = self.client.get(node_name)
        if state_retrieved == b'':
            return None
        
        return state_retrieved
        

