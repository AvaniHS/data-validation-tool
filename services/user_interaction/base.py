from abc import ABC, abstractmethod

class UserInputProvider(ABC):
    @abstractmethod
    def get_input(self, prompt: str, required: bool = True, default: str = None) -> str:
        pass 