# 加载环境变量
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
from fastapi import APIRouter, Depends, File, Form, UploadFile, Depends
from pydantic import BaseModel,Field
from typing import Any,Optional
from fastapi.responses import StreamingResponse
from controller.write_tutorial.role import TutorialAssistant
from metagpt.config2 import Config
from Utils.data_handle import insert_into_markdown
from fastapi import HTTPException


router = APIRouter()


# demand = "Write a tutorial about MySQL"
# role = TutorialAssistant(language="Chinese")


class Service:
    @classmethod
    async def create_message(cls,demand:str,model:list[str],api_key:str,document_type:str,directory:Optional[str],word_number:int):
        config = Config.config({'api_type': model[0], 'api_key': api_key, 'model': model[1]})
        role = TutorialAssistant(document_type=document_type,directory=directory,demand=demand,word_number = word_number,config=config)
        try:
            resp = await role.run(demand)
            # if demand:
            #     msg = None
            # if isinstance(demand, str):
            #         msg = Message(content=demand)
            # elif isinstance(demand, Message):
            #         msg = demand
            # elif isinstance(demand, list):
            #         msg = Message(content="\n".join(demand))
            # if not msg.cause_by:
            #         msg.cause_by = UserRequirement
            # role.put_message(msg)
            # if not await role._observe():
            #     # If there is no new information, suspend and wait
            #     # logger.debug(f"{self._setting}: no news. waiting.")
            #     return
            # # role.run(demand)
            # role._set_state(0)
            # todo = role.rc.todo
            # msg = role.rc.memory.get(k=1)[0]
            # role.demand = msg.content
            # resp = await todo.run(demand=role.demand)
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
                yield f'data:{result}\n\n'
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @classmethod
    def save_file():
        """
            存入文件
        """
        pass        

class ChatQueryModel(BaseModel):
    api_key: str = Field(default="", description="the model api_key")
    demand: str = Field(default="", description="docs demand")
    directory: str = Field(default="", description="the docs custorm directory")
    document_type: str = Field(default="", description="the docs type")
    model: list[str] = Field(default=['aa','fff'],description="model")
    wordNumber:int = Field(default=200,description="model")



@router.post("/chat/docs-agent",response_model=str)
async def root(chatQuery: ChatQueryModel):
    return StreamingResponse(Service.create_message(demand=chatQuery.demand,model =chatQuery.model,api_key=chatQuery.api_key,document_type=chatQuery.document_type,directory=chatQuery.directory,word_number = chatQuery.wordNumber ),media_type="text/event-stream")
    # return StreamingResponse(output(),
    #                         media_type="text/event-stream")
