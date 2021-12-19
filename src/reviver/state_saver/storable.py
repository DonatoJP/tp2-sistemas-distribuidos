from abc import ABC, abstractmethod

class Storable:
    def __init__(self, name) -> None:
        self.name = name

    @abstractmethod
    def export_state(self):
        pass