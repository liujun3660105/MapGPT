# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, Depends, File, Form, UploadFile, Depends
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

router = APIRouter()


class ChatQueryModel(BaseModel):
    query: str
    # collectionName: str


api_key = os.getenv('OPENAI_API_KEY')  # 设置 OpenAI 的 key
api_base = os.getenv('OPENAI_API_BASE')  # 指定代理地址
client = AsyncOpenAI(api_key=api_key, base_url=api_base)
agent = start_agent()


async def send_message(chatQuery: ChatQueryModel,
                       agent: MapGPT) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    query = chatQuery.query
    task = asyncio.create_task(agent.run(query))
    try:
        async for token in callback.aiter():
            yield token
    except Exception as e:
        print(f" Caught exception:{e}")
    finally:
        callback.done.set()
    await task


#根据文章内容对话
# @router.post("/chat/completions1")
# async def root(chatQuery: ChatQueryModel,agent = Depends(start_agent)):
#     print('chatQuery',chatQuery)
#     generator = send_message(chatQuery,agent)
#     return StreamingResponse(generator, media_type="text/event-stream")
async def message_generator():
    result = generator_msg()
    asyncio.run(result)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(result)
    # for i in range(10):
    #     yield f"data: event {i}\n\n"
    #     await asyncio.sleep(1)
async def generator_openai(msg: str):
    text = ''
    response = await client.chat.completions.create(
        stream=True,
        model="gpt-4",
        messages=[{"role":"system","content":"You are a helpful AI assistant."},{
            "role": "user",
            "content": msg
        }],
        
    )
        #     chat_completion = await self.client.chat.completions.create(
        #     messages=messages, **payload
        # )
        #     async for r in chat_completion:
        #     if len(r.choices) == 0:
        #         continue
        #     if r.choices[0].delta.content is not None:
        #         content = r.choices[0].delta.content
        #         text += content
        #         yield ModelOutput(text=text, error_code=0)
    # async with client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{
    #         "role": "user",
    #         "content": msg
    #     }],
    #     stream=True,
    # ) as response:
    
    async for chunk in response:
        if chunk.choices[0].delta.content is not None:
            # print(chunk.choices[0].delta.content, end="")
            content = chunk.choices[0].delta.content
            text +=content
            # modeloutput = ModelOutput(text=content, error_code=0)
            # print('content',text)
            text = text.replace("\n", "\\n")
            yield f'data:{text}\n\n'

async def generate_stream(msg:str):
    for s in generator_openai(msg):
        yield s

async def generator_msg():
    for i in range(10):
        yield f"data: event {i}\n\n"
        await asyncio.sleep(1)





@router.post("/chat/completions",response_model=str)
async def root(chatQuery: ChatQueryModel):
# async def root(prompt: str):
    print('chatQuery', chatQuery)

                # await asyncio.sleep(1)

    # generator = send_message(chatQuery,agent)
    return StreamingResponse(agent.run(chatQuery.query,verbose=True),
                            media_type="text/event-stream")
    return StreamingResponse(generator_openai(chatQuery.query),
                             media_type="text/event-stream")
    return StreamingResponse(generator_msg(), media_type="text/event-stream")
