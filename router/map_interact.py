# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, Depends, File, Form, UploadFile, Depends,WebSocket,WebSocketDisconnect
from pydantic import BaseModel
from typing import Any, AsyncIterable
from langchain.chat_models import ChatOpenAI
from mapagent.InitAgent import start_agent
from mapagent.MapGPT import MapGPT
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
from Utils.ws_manager import WSConnectionManager

router = APIRouter()

# global ws
# ws = None
# wsList = []
ws_manager = WSConnectionManager()
class ChatQueryModel(BaseModel):
    query: str
    client_id:str


class Service:
    @classmethod
    async def receive_message(cls,query:str,client_id:str):
        print(f'sse client_id is {client_id}')
        role = GeoAnalysisAssistant()
        res = await role.run(query) # 这是生成的sql语句
        sql_execute_result = execute_sql_search_json(res.content)
        #判断是否是geojson数据
        geojson = extract_potential_geojson(sql_execute_result)
        # ws.send()
        if geojson:
            await ws_manager.send_messages(client_id,{"data":geojson,"action":"getData","socketType":'geojson'})
            result = '获取的空间数据已经在地图上显示'
            yield f'data:{result}\n\n'
        #如果是geojson数据，则直接返回给前端
        else:
        #最后用一个action进行总结
            result = await ResultSummarizer().run(query = query,result = sql_execute_result)
            logger.info(result)
            yield f'data:{result}\n\n'      

@router.post("/chat/map-interact",response_model=str)
async def root(chatQuery: ChatQueryModel):
    return StreamingResponse(
        Service.receive_message(chatQuery.query,chatQuery.client_id),media_type="text/event-stream")


@router.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket:WebSocket,client_id:str):
    print(f'ws client_id is {client_id}',websocket)
    await ws_manager.connect(client_id=client_id,websocket=websocket)
    try:
        while True:
            data = await websocket.receive_json()
            print('data',data)
            # service.set_socketType(data['socketType'])
            
            # print('data',data)
        # await websocket.send_json({"data":{"name":"june"},"socketType":'geojson',"action":"getData"})
    except WebSocketDisconnect as err:
        print(f'{client_id} ws closed' )
        await ws_manager.disconnect(client_id=client_id)

