from abc import ABC, abstractmethod
from langchain_core.documents import Document
from typing import List
class VectorDB(ABC):
    @abstractmethod
    async def aadd_documents(self,docs:List[Document]):
        pass
    
    # @abstractmethod
    # async def aask(self,query:str):
    #     pass