# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, File, UploadFile, Form
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from metagpt.logs import logger
from config.config import Config
from controller.rag.local_file import LocalFile,FileFormat
from controller.rag.doc_qa import DocQA
from controller.rag.text_splitter import TextSplitter

CFG = Config()

router = APIRouter()

class ChatQueryModel(BaseModel):
    query: str #提问内容
    # file_id: str ## 针对哪个文件进行提问
    
doc_qa = DocQA()

class FileParserModel(BaseModel):
    file_id:str
    file_format:str
    file_path:str
    file_name:str

@router.post("/rag/file_parser")
async def root(parserQuery:FileParserModel):
    file_id = parserQuery.file_id
    file_name = parserQuery.file_name
    file_format = parserQuery.file_format
    file_path = parserQuery.file_path
    # print('file',file,fileFormat,fileId)
    # file_name = file.filename
    # file_content = await file.read()
    try:
        local_file = LocalFile(file_id=file_id,file_name =file_name ,file_format=file_format,file_path=file_path,text_splitter=TextSplitter.get_text_splitter('recursive_char_text_splitter'))
        local_file.save_file()
        await doc_qa.add_local_file(local_file)
    except Exception as e:
        logger.debug((f"load document has error: {e}"))
        raise HTTPException(status_code=500, detail=f"load document has error: {e}")
    return {"uploadStatus": 'success'}


@router.post("/rag/chat")
async def root(chatQuery:ChatQueryModel):
    # field_id = chatQuery.file_id
    query = chatQuery.query
    return StreamingResponse(doc_qa.aask_custom_chain(query=query),media_type="text/event-stream")
    
    
    
    

    


