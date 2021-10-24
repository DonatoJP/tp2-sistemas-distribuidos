from abc import ABC, abstractmethod

class AbstractOperator:
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def exec_operation(self, data, **kwargs) -> list:
        pass