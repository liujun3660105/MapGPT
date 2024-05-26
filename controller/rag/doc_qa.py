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
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.prompts import PromptTemplate
from langchain.chains import (ConversationalRetrievalChain)
from langchain_core.runnables import RunnablePassthrough
import asyncio
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from llm.langchain.qianwen import ChatDashScope
from llm.langchain.tongyi import Tongyi
# from langchain.llms.openai import OpenAI
from langchain_openai import ChatOpenAI
from controller.rag.local_rerank import LocalRerankBackend
from Utils.decrator import get_time

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
        self.memory = ConversationBufferMemory(memory_key="chat_history",
                                               return_messages=True,
                                               return_source_documents=True)
        self.local_rerank_backend = LocalRerankBackend()

        self.graph = Neo4jGraph(url=CFG.NEO4J_URL,
                                password=CFG.NEO4J_PASSWORD,
                                username=CFG.NEO4J_USERNAME)
        # graph_llm = Tongyi(dashscope_api_key=CFG.DASHSCOPE_API_KEY)
        graph_llm = ChatOpenAI(openai_proxy=CFG.OPENAI_API_BASE,api_key=CFG.OPENAI_API_KEY)
        self.llm_transformer = LLMGraphTransformer(llm=graph_llm)

    async def add_local_file(self, local_file: LocalFile):
        local_file.split_file_to_document()
        await self.vector_db.aadd_documents(local_file.docs)
        graph_documents =await self.llm_transformer.aconvert_to_graph_documents(
            local_file.docs)
        self.graph.add_graph_documents(graph_documents,
                                       baseEntityLabel=True,
                                       include_source=True)

    async def aask(self, query: str):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        llm = ChatDashScope(api_key=CFG.DASHSCOPE_API_KEY,
                            callbacks=[callback])
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

    @get_time
    async def similar_search(self, query: str) -> str:
        # 根据问题进行相似性检索，并通过rerank进行重排，返回结果融合后的字符串
        docs: List[Document] = await self.vector_db.aquery_documents(query,
                                                                     top_k=5)
        similar_str_list = map(lambda x: x.page_content, docs)
        scores = self.local_rerank_backend.predict(query, similar_str_list)
        for idx, score in enumerate(scores):
            docs[idx].metadata['score'] = score
        source_documents = sorted(docs,
                                  key=lambda x: x.metadata['score'],
                                  reverse=True)
        return self.format_docs(source_documents)

    async def aask_custom_chain(self, query: str):
        similar_str = await self.similar_search(query)
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                           qianfan_ak=CFG.BAIDU_API_KEY,
        #                           qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                           streaming=True,
        #                           callbacks=[callback])
        llm = Tongyi(dashscope_api_key=CFG.DASHSCOPE_API_KEY,
                     streaming=True,
                     callbacks=[callback])
        prompt = PromptTemplate(input_variables=["query"],
                                template=RAG,
                                partial_variables={
                                    "chatHistory":
                                    self.memory.load_memory_variables({}),
                                    "context":
                                    similar_str
                                })
        chain = ({
            # "context":
            # self.vector_db.vector_db.as_retriever() | self.format_docs,
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
        llm = Tongyi(dashscope_api_key=CFG.DASHSCOPE_API_KEY,
                     streaming=True,
                     callbacks=[callback])

        prompt = PromptTemplate(input_variables=[
            "context",
            "query",
        ],
                                template=RAG,
                                partial_variables={
                                    "chatHistory":
                                    self.memory.load_memory_variables({})
                                })
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
