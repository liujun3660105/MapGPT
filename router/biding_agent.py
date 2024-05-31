# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from fastapi import HTTPException
from mapagent.MapGPT import MapGPT
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
import asyncio
from controller.map_interact.action import ResultSummarizer
from metagpt.logs import logger
from PyPDF2 import PdfReader,PdfFileReader
from langchain.text_splitter import CharacterTextSplitter,RecursiveCharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from Utils.device import get_device
from config.config import Config
from langchain.schema import Document
from controller.biding_qa.role import BidingAssistant
from Utils.const import get_root_path
from datasource.vector_db.chromadb import ChromaDB,FileType
from enum import Enum
from controller.biding_qa.action import RAGRetriever

CFG = Config()

router = APIRouter()

role = BidingAssistant()

vector_db = ChromaDB()

class ChatQueryModel(BaseModel):
    query: str #提问内容
    file_id: str ## 针对哪个文件进行提问

retriever = RAGRetriever(vector_db)


async def send_message(query:str):
    callback = AsyncIteratorCallbackHandler()
    result = await retriever.aask(query)
    yield result


@router.post("/biding_agent/upload_file")
async def root(file: UploadFile = File(...),fileType:FileType = Form(...),fileId:str = Form(...)):
    try:
        psf_reader = PdfReader(file.file)
        text = ""
        for index,page in enumerate(psf_reader.pages):
            print(page,index)
            text += page.extract_text()
        text=text.replace("[", "").replace("]", "")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200,
                                            chunk_overlap=20,
                                            separators=["\n\n", "\n", " ", ""],
                                            length_function=len)
        text_list = text_splitter.split_text(text)
        docs =list(map(lambda x:Document(page_content=x,metadata = {"page":index+1,"file_id":fileId}),text_list) 
        ) 
        print('docs',docs)
        
        await vector_db.aadd_documents(fileType,docs)
        result = await vector_db.asimilarity_search('尿酸多高',k=2)
        print('result',result)
    except Exception as e:
        logger.debug((f"load document has error: {e}"))
        raise HTTPException(status_code=500, detail=f"load document has error: {e}")
    return {"uploadStatus": 'success'}


@router.post("/biding_agent/chat")
async def root(chatQuery:ChatQueryModel):
    field_id = chatQuery.file_id
    query = chatQuery.query
    return StreamingResponse(send_message(query=query),media_type="text/event-stream")
    
    
    
    

    


