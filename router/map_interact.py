# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, Depends, File, Form, UploadFile, Depends
from pydantic import BaseModel
from typing import Any, AsyncIterable
from langchain.chat_models import ChatOpenAI
from MapAgent.InitAgent import start_agent
from MapAgent.MapGPT import MapGPT
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
import asyncio
from openai import OpenAI,AsyncOpenAI
import os
from Utils.output import ModelOutput
from controller.map_interact.role import GeoAnalysisAssistant
from Tools.SqlTool import SqlAnalyser
from Tools.DataBaseTool import execute_sql_search_json
from controller.map_interact.action import ResultSummarizer
from metagpt.logs import logger
from Utils.data_handle import extract_potential_geojson
import json

router = APIRouter()

class ChatQueryModel(BaseModel):
    query: str


class Service:
    @classmethod
    async def receive_message(cls,query:str):
        role = GeoAnalysisAssistant()
        res = await role.run(query) # 这是生成的sql语句
        sql_execute_result = execute_sql_search_json(res.content)
        #判断是否是geojson数据
        geojson = extract_potential_geojson(sql_execute_result)
        if geojson:
            result = '获取的空间数据为:'+json.dumps(geojson)
            yield f'data:{result}\n\n'
        #如果是geojson数据，则直接返回给前端
        else:
        #最后用一个action进行总结
            result = await ResultSummarizer().run(query = query,result = sql_execute_result)
            logger.info(result)
            yield f'data:{result}\n\n'

@router.post("/chat/map-interact",response_model=str)
async def root(chatQuery: ChatQueryModel):
    return StreamingResponse(Service.receive_message(chatQuery.query),media_type="text/event-stream")

