
from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from controller.teacher_agent.index import TeacherAgent
from langchain.callbacks import AsyncIteratorCallbackHandler
import asyncio

class ChatQueryModel(BaseModel):
    query: str #提问内容

router = APIRouter()

callback = AsyncIteratorCallbackHandler()
teacher_agent = TeacherAgent(callback=callback)
chain = teacher_agent.chain

async def send_message(query:str):

    
    # result = await teacher_agent.run(query)
    # yield result
    response = ''
    task = asyncio.create_task(chain.apredict(input=query))
    try:
        async for token in callback.aiter():
            print('token',token)
            response += token
            response_text = response.replace("\n", "\\n")
            yield f'data: {response_text}\n\n'
            # yield token
    except Exception as e:
        print(f" Caught exception:{e}")
    finally:
        callback.done.set()
    await task

    # yield ''


@router.post("/teacher_agent/chat")
async def root(chatQuery:ChatQueryModel):
    query = chatQuery.query
    return StreamingResponse(teacher_agent.generate_stream_conversation_chain(query=query),media_type="text/event-stream")