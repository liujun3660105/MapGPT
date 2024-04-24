from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from Utils.device import get_device
from config.config import Config
from typing import List, Dict, Union
from controller.rag.local_file import LocalFile
from controller.rag.prompt import RAG

from datasource.vector_db.milvus import MilvusClient
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import (ConversationalRetrievalChain)
from langchain_core.runnables import RunnablePassthrough
import asyncio
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from llm.langchain.qianwen import ChatDashScope
from llm.langchain.tongyi import Tongyi



CFG = Config()


class DocQA:

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=CFG.EMBEDDING_PATH,
            model_kwargs={'device': get_device()},
            encode_kwargs={'normalize_embeddings': False})
        self.vector_db = MilvusClient(host=CFG.MILVUS_HOST,
                                      port=CFG.MILVUS_PORT,
                                      user=CFG.MILVUS_USERNAME,
                                      password=CFG.MILVUS_PASSWORD,
                                      embeddings=self.embeddings)
        # self.local_file: List[LocalFile] = []
        self.memory = ConversationBufferMemory(memory_key="chat_history",
                                               return_messages=True,
                                               return_source_documents=True)
        # callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        # self.chain = ConversationalRetrievalChain.from_llm(llm = llm,verbose=True,retriever=self.vector_db.vector_db.as_retriever(),memory=self.memory)

    async def add_local_file(self, local_file: LocalFile):
        local_file.split_file_to_document()
        # local_file.save_to_vectordb(self.vector_db)
        await self.vector_db.aadd_documents(local_file.docs)
        # self.local_file.append(local_file)

    async def aask(self, query: str):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        llm = ChatDashScope(api_key=CFG.DASHSCOPE_API_KEY,callbacks=[callback])
        # prompt = PromptTemplate(input_variables=["history", "input"], template=RAG)
        # memory = ConversationBufferMemory(memory_key="chat_history",
        #                             return_messages=True)
        # chain = (prompt|llm|StrOutputParser())
        # chain = ConversationalRetrievalChain(
        #     # prompt=prompt,
        #     llm=llm,
        #     verbose=True,
        #     retriever=self.vector_db.vector_db.as_retriever(),
        #     memory=self.memory,
        # )
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            verbose=True,
            retriever=self.vector_db.vector_db.as_retriever(),
            memory=self.memory)

        content = ''
        run = asyncio.create_task(chain.ainvoke({'question': query}))
        async for token in callback.aiter():
            print('token', token)
            content += token
            response_text = content.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
        await run

    def format_docs(self, docs: List[Document]):
        return "\n\n".join(doc.page_content for doc in docs)

    async def aask_custom_chain(self, query: str):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        llm = Tongyi(dashscope_api_key=CFG.DASHSCOPE_API_KEY,streaming=True,callbacks=[callback])
        prompt = PromptTemplate(
            input_variables=["context", "query", ], template=RAG,partial_variables={"chatHistory":self.memory.load_memory_variables({})})
        chain = ({
            "context":
            self.vector_db.vector_db.as_retriever() | self.format_docs,
            # "chatHistory": lambda x:x['chatHistory'],
            "query": RunnablePassthrough(),
            # "query": lambda x: x["query"],
        } | prompt | llm | StrOutputParser())
        print('chatHistory', self.memory.load_memory_variables({}))
        print('query', query)
        run = asyncio.create_task(chain.ainvoke(query))
        content = ''
        async for token in callback.aiter():
            print('token', token)
            content += token
            response_text = content.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
        self.memory.save_context({"user": query}, {"you": content})
        await run
        
    async def aask_custom_multi_chain(self, query: str):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        # llm = ChatDashScope(api_key=CFG.DASHSCOPE_API_KEY,callbacks=[callback])
        llm = Tongyi(dashscope_api_key=CFG.DASHSCOPE_API_KEY,streaming=True,callbacks=[callback])
        
        prompt = PromptTemplate(
            input_variables=["context", "query", ], template=RAG,partial_variables={"chatHistory":self.memory.load_memory_variables({})})
        chain = ({
            "context":
            self.vector_db.vector_db.as_retriever() | self.format_docs,
            # "chatHistory": lambda x:x['chatHistory'],
            "query": RunnablePassthrough()
            # "query": lambda x: x["query"],
        } | prompt | llm | StrOutputParser())
        print('chatHistory', self.memory.load_memory_variables({}))
        print('query', query)
        run = asyncio.create_task(chain.ainvoke(query))
        content = ''
        async for token in callback.aiter():
            print('token', token)
            content += token
            response_text = content.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
        self.memory.save_context({"user": query}, {"you": content})
        await run