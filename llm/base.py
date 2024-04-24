from abc import ABC, abstractmethod
class BaseLLM(ABC):
    temperature: float = 0
    max_tokens: int = 50
    streaming: bool = True
    @abstractmethod
    def generate_text(self, prompt):
        pass