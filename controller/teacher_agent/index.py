from typing import List, Optional, Tuple, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.llms import BaseLLM
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain.chains import (StuffDocumentsChain, LLMChain,
                              ConversationalRetrievalChain, ConversationChain)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.output_parser import StrOutputParser
from .prompt import template
from pydantic import BaseModel, Field
from config.config import Config
import asyncio
from langchain.chat_models.openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from llm.langchain.qianwen import ChatDashScope

CFG = Config()


class TeacherAgent(BaseModel):
    # llm:Optional[BaseLLM] = Field(default_factory=QianfanChatEndpoint(model_name='ERNIE-4.0-8K',qianfan_ak=CFG.BAIDU_API_KEY, qianfan_sk=CFG.BAIDU_SECRET_KEY,streaming=True,callbacks=[StreamingStdOutCallbackHandler()]))
    name: Optional[str] = 'June'
    role: Optional[str] = '经验丰富的老师，善于教导学生'
    callback: Any = AsyncIteratorCallbackHandler()
    memory:ConversationBufferMemory = ConversationBufferMemory()
    # prompt:PromptTemplate = Field(default_factory=PromptTemplate(input_variables=["history", "input"], template=template))

    # callback:Field(default_factory=AsyncIteratorCallbackHandler())
    # def __init__(self):
    #     PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    #     self.conversationChain = ConversationChain(
    #         prompt=PROMPT,
    #         llm=self.llm,
    #         verbose=True,
    #         memory=ConversationBufferMemory(ai_prefix="AI Teacher",human_prefix="Student"),
    #     )
    @property
    def chain(self):
        callback = AsyncIteratorCallbackHandler()
        # self.callback = AsyncIteratorCallbackHandler()
        llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
                                  qianfan_ak=CFG.BAIDU_API_KEY,
                                  qianfan_sk=CFG.BAIDU_SECRET_KEY,
                                  streaming=True,
                                  callbacks=[callback])
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        # prompt = ChatPromptTemplate.from_messages([
        #     SystemMessagePromptTemplate.from_template(
        #         "You're a AI that knows everything about cats."),
        #     MessagesPlaceholder(variable_name="history"),
        #     HumanMessagePromptTemplate.from_template("{input}"),
        # ])
        chain = (prompt|llm|StrOutputParser())
        return chain
        return ConversationChain(
            # prompt=prompt,
            llm=llm,
            verbose=True,
            # memory=ConversationBufferMemory(ai_prefix="AI Teacher",human_prefix="Student"),
            memory=ConversationBufferMemory(),
        )

    async def generate_stream_custom_chain(self, query):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                     qianfan_ak=CFG.BAIDU_API_KEY,
        #                     qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                     streaming=True,
        #                     callbacks=[callback])
    #     llm = ChatOpenAI(
    #         openai_proxy=CFG.OPENAI_API_BASE,
    #         openai_api_key = CFG.OPENAI_API_KEY,
    #         model="gpt-4-1106-preview",
    #         temperature=0,
    #         streaming=True,
    #         model_kwargs={
    #             "seed": 42,
    #         },
            
    #     callbacks = [callback]
    # )
        llm = ChatDashScope(api_key=CFG.DASHSCOPE_API_KEY,
                            callbacks=[callback])
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        chain = (prompt|llm|StrOutputParser())
        content = ''
        print('history',self.memory.load_memory_variables({}))
        print('query',query)
        run = asyncio.create_task(chain.ainvoke({
            "history":self.memory.load_memory_variables({}),
            "input":query
        }))
        async for token in callback.aiter():
            print('token',token)
            content += token
            response_text = content.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
        self.memory.save_context({"student":query},{"ai teacher":content})
        await run
    async def generate_stream_conversation_chain(self, query):
        callback = AsyncIteratorCallbackHandler()
        # llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',
        #                     qianfan_ak=CFG.BAIDU_API_KEY,
        #                     qianfan_sk=CFG.BAIDU_SECRET_KEY,
        #                     streaming=True,
        #                     callbacks=[callback])
        llm = ChatOpenAI(
            openai_proxy=CFG.OPENAI_API_BASE,
            openai_api_key = CFG.OPENAI_API_KEY,
            model="gpt-4-1106-preview",
            temperature=0,
            streaming=True,
            model_kwargs={
                "seed": 42,
            },
            
            
        callbacks = [callback]
    )
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        # chain = (prompt|llm|StrOutputParser())
        chain = ConversationChain(
            prompt=prompt,
            llm=llm,
            verbose=True,
            # memory=ConversationBufferMemory(ai_prefix="AI Teacher",human_prefix="Student"),
            memory=self.memory,
        )
        
        content = ''
        print('history',self.memory.load_memory_variables({}))
        print('query',query)
        # run = asyncio.create_task(chain.ainvoke({
        #     "history":self.memory.load_memory_variables({}),
        #     "input":query
        # }))
        run = asyncio.create_task(chain.arun(input=query))
        async for token in callback.aiter():
            print('token',token)
            content += token
            response_text = content.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
        # self.memory.save_context({"student":query},{"ai teacher":content})
        await run