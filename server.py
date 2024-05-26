# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from config.config import Config,WebServerParameters
import argparse
import os
import sys
from typing import List

from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from Utils.logUtils import logging_str_to_uvicorn_level,setup_logging,_get_logging_level
from MapAgent.InitAgent import start_agent

from router import chat
from router import docs_agent
from router import map_interact
from router import biding_agent,teacher_agent,rag,vl
import websockets
import asyncio

origins = ["*"]

app = FastAPI(
    title="MapGPT OPEN API",
    description="This is mapgpt, with auto docs for the API and everything",
    version="0.5.0",
    openapi_tags=[],
)


async def hello(websocket,path):
    name = await websocket.recv()
    print('receive_name',name)
    await websocket.send('hello, '+name)

def start_ws(ws_func):
    start_ws_server = websockets.serve(ws_func, "localhost", 8123)
    print('start_ws_server',start_ws_server)
    asyncio.get_event_loop().run_until_complete(start_ws_server)
    asyncio.get_event_loop().run_forever()

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
        # allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



def mount_routers(app: FastAPI):
    """Lazy import to avoid high time cost""" 
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    app.include_router(docs_agent.router, prefix="/api/v1", tags=["chat"])
    app.include_router(map_interact.router, prefix="/api/v1", tags=["chat"])
    app.include_router(biding_agent.router, prefix="/api/v1", tags=["chat"])
    app.include_router(teacher_agent.router, prefix="/api/v1", tags=["chat"])
    app.include_router(rag.router, prefix="/api/v1", tags=["chat"])
    app.include_router(vl.router, prefix="/api/v1", tags=["chat"])

def run_uvicorn(param: WebServerParameters):
    import uvicorn

    uvicorn.run(
        app,
        host=param.host,
        port=param.port,
        log_level=logging_str_to_uvicorn_level(param.log_level),
    )
    
def _get_webserver_params(args: List[str] = None):
    from Utils.parameterUtils import EnvArgumentParser

    parser: argparse.ArgumentParser = EnvArgumentParser.create_argparse_option(
        WebServerParameters
    )
    # aa = vars(parser.parse_args(args=args))
    # print(aa)
    return WebServerParameters(**vars(parser.parse_args(args=args))) 

    


def run_webserver(param: WebServerParameters = None):
    if not param:
        param = _get_webserver_params()
        
    if not param.log_level:
        param.log_level = _get_logging_level()
        setup_logging(
            "mapgpt", logging_level=param.log_level, logger_filename=param.log_file
        )

    mount_routers(app) # 注册路由
    # start_ws(hello)
    run_uvicorn(param)
    


# @app.get('/')
# async def root():
#     return {'message': 'Hello World'}


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")
        
run_webserver()
