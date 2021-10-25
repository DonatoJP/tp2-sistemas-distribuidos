from abc import ABC, abstractmethod

class AbstractHolder:
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def exec_operation(self, data, **kwargs) -> list:
        pass

    @abstractmethod
    def end(self):
        pass