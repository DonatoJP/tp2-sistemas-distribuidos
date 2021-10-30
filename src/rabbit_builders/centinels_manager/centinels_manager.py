class CentinelsManager:
    def __init__(self, previous_step_components) -> None:
        self.previous_step_components = previous_step_components
        self.received_centinels = 0
        self._centinel = 'END'

    def is_centinel(self, message):
        return message == self.centinel
    
    def count_centinel(self):
        self.received_centinels += 1
    
    def are_all_received(self):
        return self.received_centinels == self.previous_step_components
    
    @property
    def centinel(self):
        return self._centinel