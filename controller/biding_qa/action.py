from metagpt.actions import Action
from typing import Dict
from .prompt import RAG
from chromadb import Client
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchain.chains import (
    StuffDocumentsChain, LLMChain, ConversationalRetrievalChain
)
from langchain.memory import ConversationBufferMemory
from config.config import Config
# from langchain_community.vectorstores.chroma import Chroma
from datasource.vector_db.chromadb import ChromaDB
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

CFG = Config()

class Retriever(Action):
    """retrieve the relevant texts from vector db based on user requirements.

    Args:
        directory: The output of the write-directory action.
        language: The language to output, default is "Chinese".
    """

    name: str = "Retriever"
    language: str = "Chinese"

    async def run(self, query: str, *args, **kwargs) -> Dict:
        """Execute the action to review the directory according to the demand and output the standard content

        Args:
            query: user query.

        Returns:
            the related document retrieved by user
        """
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory).format(demand=demand, language=self.language,direcotry = self.directory)
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory)
        # prompt = prompt.format(demand=demand, language=self.language, aa = self.directory)
        # prompt = RAG.format(directory=directory)
        # resp = await self._aask(prompt=prompt)
        # resp = resp.replace('\n','')
        # return OutputParser.extract_struct(resp, list)
    
    
    
    
class RAGRetriever():
    vector_db:ChromaDB
    def __init__(self,vector_db:ChromaDB) -> None:
        self.vector_db = vector_db

# This controls how the standalone question is generated.
# Should take `chat_history` and `question` as input variables.
# template = (
#     "Combine the chat history and follow up question into "
#     "a standalone question. Chat History: {chat_history}"
#     "Follow up question: {question}"
# )
    async def aask(self,query:str):
        result =await self.vector_db.asimilarity_search(query)
        print('query result',result)
        prompt = PromptTemplate.from_template(RAG)
        memory = ConversationBufferMemory(memory_key="chat_history",
                                            return_messages=True)
        llm = QianfanChatEndpoint(model_name='ERNIE-4.0-8K',qianfan_ak=CFG.BAIDU_API_KEY, qianfan_sk=CFG.BAIDU_SECRET_KEY,streaming=True,callbacks=[StreamingStdOutCallbackHandler()])
        question_generator_chain = LLMChain(llm=llm, prompt=prompt)
        # chain = ConversationalRetrievalChain(
        #     retriever=self.vector_db.get_current_vectordb.as_retriever(),
        #     question_generator=question_generator_chain,
        #     memory=memory
        # )
        chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=self.vector_db.get_current_vectordb.as_retriever(),
            memory = memory
        )
        content = ''
        async for s in chain.astream({"question": query}):
            print(s)
            # content += s

        return content
        
