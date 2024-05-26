
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import asyncio
from controller.pic_check.index import PicCheck
import os

class ChatQueryModel(BaseModel):
    query: str #提问内容
    right_answer_url:str # 正确答案图片链接
    student_answer_url:str # 学生答题图片链接

router = APIRouter()


pic_check = PicCheck()

@router.post("/vl/check_by_pic")
async def root(chatQuery:ChatQueryModel):
    right_answer_url = chatQuery.right_answer_url
    student_answer_url = chatQuery.student_answer_url
    query = chatQuery.query
    response = pic_check.check(right_answer_url,student_answer_url)
    return response
    