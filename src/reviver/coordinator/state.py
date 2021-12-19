import os
import pickle

from vault.client import VaultClient
import os

filename = "state.txt"


class State:
    def __init__(self):
        rabbit_addr = os.getenv('RABBIT_ADDRESS')
        vault_input_queue_name = os.getenv('VAULT_INPUT_QUEUE_NAME')
        self.vault = VaultClient(rabbit_addr, vault_input_queue_name)

    def get(self, key):
        return self.vault.get(key)

    def set(self, key, val):
        self.vault.post(key, val)

    def set_k(self, key1, key2, val):
        self.vault.post_key(key1, key2, val)

    def get_k(self, key1, key2):
        return self.vault.get_key(key1, key2)

    def remove_k(self, key1, key2):
        self.vault.post_key(key1, key2, "")
