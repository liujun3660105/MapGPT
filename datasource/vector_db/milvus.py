from langchain_community.vectorstores.milvus import Milvus
from langchain_core.documents import Document
from pydantic import BaseModel,Field
from typing import Any,List
from datasource.vector_db.base import VectorDB
class MilvusClient(BaseModel,VectorDB):
    host:str
    port:int
    user:str
    password:str
    secure:bool = False
    embeddings:Any #FIXME:这个类型补充进来
    collection_name:str = "my_collection"
    # vector_db:Milvus = Milvus(embedding_function=embeddings, host=host, port=port, user=user, password=password, secure=secure,collection_name=collection_name)
    # def __init__(self):
    #     self.vector_db = Milvus(embedding_function=self.embeddings, host=self.host, port=self.port, user=self.user, password=self.password, secure=self.secure,collection_name=self.collection_name)

    @property
    def vector_db(self):
        return Milvus(embedding_function=self.embeddings,connection_args = {
            'host':self.host, 'port':self.port, 'user':self.user, 'password':self.password,'secure':self.secure},collection_name=self.collection_name,auto_id=True)
    
    def create_collection(self, collection_name, fields):
        # 创建集合的逻辑
        print(f"Creating collection '{collection_name}' with fields: {fields}")

    async def aadd_documents(self,docs:List[Document]):
        await self.vector_db.aadd_documents(docs)
    def insert_vectors(self, collection_name, vectors):
        # 插入向量的逻辑
        print(f"Inserting vectors into collection '{collection_name}'")