
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
from llm.llm_for_online import OpenAILLM
import os

class ChatQueryModel(BaseModel):
    query: str #提问内容
    image:str # 图片链接

router = APIRouter()

llm = OpenAILLM(api_key=os.getenv('OPENAI_API_KEY'),base_url = os.getenv('OPENAI_API_BASE'),model='gpt-4o')
async def send_message(query:str,image:str):
    print('query,query,image',query,image)
    text = ''
    async for chunk in llm.generate_text_stream(query=query,image=image):
        text +=chunk
        text = text.replace("\n", "\\n")
        yield f'data:{text}\n\n'



@router.post("/vl/chat")
async def root(chatQuery:ChatQueryModel):
    query = chatQuery.query
    image = chatQuery.image
    return StreamingResponse(send_message(query,image),media_type="text/event-stream")