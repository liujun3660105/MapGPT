
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
from controller.audio_check.index import AudioCheck
import os

class ChatQueryModel(BaseModel):
    query: str #提问内容
    audio_url:str # 音频文件链接

router = APIRouter()

audio_check = AudioCheck()


@router.post("/audio/check_by_audio")
async def root(chatQuery:ChatQueryModel):
    query = chatQuery.query
    audio_url = chatQuery.audio_url
    response = audio_check.check(query=qeury,audio_url=audio_url)
    return response