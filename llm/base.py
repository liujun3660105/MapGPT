from abc import ABC, abstractmethod
from pydantic import BaseModel
class BaseLLM(BaseModel,ABC):
    @abstractmethod
    def generate_text(self, messages:list[dict],timeout=3):
        pass