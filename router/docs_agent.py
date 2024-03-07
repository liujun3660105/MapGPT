# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, Depends, File, Form, UploadFile, Depends
from pydantic import BaseModel
from typing import Any
from fastapi.responses import StreamingResponse
import asyncio
from controller.write_tutorial.role import TutorialAssistant
from metagpt.schema import Message, MessageQueue, SerializationMixin
from metagpt.actions.add_requirement import UserRequirement
from Utils.data_handle import insert_into_markdown

router = APIRouter()


topic = "Write a tutorial about MySQL"
role = TutorialAssistant(language="Chinese")


class Service:
    @classmethod
    async def create_message(cls,with_message:str):
        role = TutorialAssistant()
        role.run()
        if with_message:
            msg = None
        if isinstance(with_message, str):
                msg = Message(content=with_message)
        elif isinstance(with_message, Message):
                msg = with_message
        elif isinstance(with_message, list):
                msg = Message(content="\n".join(with_message))
        if not msg.cause_by:
                msg.cause_by = UserRequirement
        role.put_message(msg)
        if not await role._observe():
            # If there is no new information, suspend and wait
            # logger.debug(f"{self._setting}: no news. waiting.")
            return
        # role.run(topic)
        role._set_state(0)
        todo = role.rc.todo
        msg = role.rc.memory.get(k=1)[0]
        role.topic = msg.content
        resp = await todo.run(topic=role.topic)
        await role._handle_directory(resp)
        
        start_idx = role.rc.state if role.rc.state >= 0 else 0
        total_content = role.total_content
        
        for i in range(start_idx, len(role.states)):
            role._set_state(i)
            current_section = role.rc.todo.current_section
            rsp = await role._act() ## 这里是每个action输出的小节内容，需要把当前小节内容插入到主目录的对应为止，初始目录内容是self.total_content
            total_content = insert_into_markdown(total_content,current_section,f"\n{rsp.content}\n")
            # if rsp.content:
            #     total_content += rsp.content
            result = total_content.replace("\n", "\\n")
            print('rsp',result)
            yield f'data:{result}\n\n'
    @classmethod
    def save_file():
        """
            存入文件
        """
        pass        
    # async def _act_by_order(self) -> Message:
    #     """switch action each time by order defined in _init_actions, i.e. _act (Action1) -> _act (Action2) -> ..."""
    #     start_idx = self.rc.state if self.rc.state >= 0 else 0  # action to run from recovered state
    #     rsp = Message(content="No actions taken yet")  # return default message if actions=[]
    #     for i in range(start_idx, len(self.states)):
    #         self._set_state(i)
    #         rsp = await self._act()
    #     return rsp  # return output from the last action

class ChatQueryModel(BaseModel):
    query: str

async def output():
    tasks = [asyncio.create_task(generator_msg()),asyncio.create_task(generator_msg()),asyncio.create_task(generator_msg())]
    done,pending = await asyncio.wait(tasks)
    for task in done:
        yield task.result()
    # for task in tasks:
    #     result =await task
    #     yield result
        
    # while True:
    #     print('loop')
    #     await task
    #     # print('result',result)
    #     yield 'ffff'
    #     if task.done():
    #         print('done')
    #         break
        

async def generator_msg():
    # print('1111')
    a = 0
    for i in range(10):
        a+=i
        # yield f"data: event {i}\n\n"
        await asyncio.sleep(1)
    return a
        

@router.post("/chat/docs-agent",response_model=str)
async def root(chatQuery: ChatQueryModel):
    print('chatQuery', chatQuery)
    return StreamingResponse(Service.create_message(with_message=topic),media_type="text/event-stream")
    return StreamingResponse(output(),
                            media_type="text/event-stream")
