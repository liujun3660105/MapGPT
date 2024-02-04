from config.config import Config,WebServerParameters
import argparse
import os
import sys
from typing import List

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from Utils.logUtils import logging_str_to_uvicorn_level,setup_logging,_get_logging_level

CFG = Config()

origins = ["*"]

app = FastAPI(
    title="MapGPT OPEN API",
    description="This is mapgpt, with auto docs for the API and everything",
    version="0.5.0",
    openapi_tags=[],
)

# 添加跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def mount_routers(app: FastAPI):
    """Lazy import to avoid high time cost"""
    # from dbgpt.app.knowledge.api import router as knowledge_router
    # from dbgpt.app.llm_manage.api import router as llm_manage_api
    # from dbgpt.app.openapi.api_v1.api_v1 import router as api_v1
    # from dbgpt.app.openapi.api_v1.editor.api_editor_v1 import (
    #     router as api_editor_route_v1,
    # )
    # from dbgpt.app.openapi.api_v1.feedback.api_fb_v1 import router as api_fb_v1

    # app.include_router(api_v1, prefix="/api", tags=["Chat"])
    # app.include_router(api_editor_route_v1, prefix="/api", tags=["Editor"])
    # app.include_router(llm_manage_api, prefix="/api", tags=["LLM Manage"])
    # app.include_router(api_fb_v1, prefix="/api", tags=["FeedBack"])

    # app.include_router(knowledge_router, tags=["Knowledge"])

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
    aa = vars(parser.parse_args(args=args))
    print(aa)
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
    run_uvicorn(param)
if __name__ == "__main__":
    run_webserver()
