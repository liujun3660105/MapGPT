from chromadb import Client
from pydantic import Field,BaseModel
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from Utils.device import get_device
from config.config import Config
from Utils.const import get_root_path
from enum import Enum
class FileType(Enum):
    """
    file type
    """
    BIDING='biding'
    TENDERING='tendering'

CFG = Config()

model_kwargs = {'device': get_device()}
encode_kwargs = {'normalize_embeddings': False}
hf_embeddings = HuggingFaceEmbeddings(
    model_name=CFG.EMBEDDING_PATH,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)



    

class ChromaDB():
    qa_biding_vectordb:Chroma= Field(default_factory=Chroma())
    qa_tending_vectordb:Chroma= Field(default_factory=Chroma())
    current_vectordb:Chroma= Field(default_factory=Chroma())
    file_type:FileType=FileType.TENDERING
    def __init__(self):
        self.qa_biding_vectordb = Chroma(collection_name='qa_biding_file_collection',embedding_function=hf_embeddings,persist_directory=f"{get_root_path()}/data/vectordb/biding")
        self.qa_biding_vectordb.persist()
        self.qa_tending_vectordb = Chroma(collection_name='qa_tending_file_collection',embedding_function=hf_embeddings,persist_directory=f"{get_root_path()}/data/vectordb/tending")
        self.qa_tending_vectordb.persist()
        
    @property
    def get_current_vectordb(self):
        print('self.file_type',self.file_type)
        if self.file_type == FileType.BIDING:
            return self.qa_biding_vectordb
        elif self.file_type == FileType.TENDERING:
            return self.qa_tending_vectordb
        
    async def aadd_documents(self,file_type:FileType,documents:list[Document]):
        self.file_type = file_type
        current_vectordb = self.get_current_vectordb
        await current_vectordb.aadd_documents(documents)
    
    async def aadd_texts(self,file_type:FileType,texts:list[str]):
        self.file_type = file_type
        current_vectordb = self.get_current_vectordb
        await current_vectordb.aadd_texts(texts)
        
    async def asimilarity_search(self,query:str,k:int=10,):
        current_vectordb = self.get_current_vectordb
        result = await current_vectordb.asimilarity_search(query=query,k=k)
        return result