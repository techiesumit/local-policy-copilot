from abc import ABC, abstractmethod

class ModelProvider(ABC):
    @abstractmethod
    def chat(self, user_text: str) -> str:
        pass
    
