from llm.base import BaseLLM
from pydantic import BaseModel,model_validator,field_validator
from openai import OpenAI,APIConnectionError,AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types import CompletionUsage
from openai._base_client import AsyncHttpxClientWrapper
from typing import Optional,Any,Union
from Utils.common import decode_image

class LLMOnline(BaseLLM):
    api_key:str = "sk-"
    base_url: str = "https://api.openai.com/v1"
    api_version: Optional[str] = None
    model:str
    aclient:Optional[Any] = None
    
    # For Cloud Service Provider like Baidu/ Alibaba
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    endpoint: Optional[str] = None  # for self-deployed model on the cloud
    
    # For Chat Completion
    max_token: int = 4096
    temperature: float = 0.0
    top_p: float = 1.0
    top_k: int = 0
    
    timeout: int = 60
    
    
    @field_validator("api_key")
    @classmethod
    def check_llm_key(cls, v):
        if v in ["", None, "YOUR_API_KEY"]:
            raise ValueError("Please set your API key for online llm")
        return v
    def _user_msg(self, msg: str, images: Optional[Union[str, list[str]]] = None) -> dict[str, Union[str, dict]]:
        if images:
            # as gpt-4v, chat with image
            return self._user_msg_with_imgs(msg, images)
        else:
            return {"role": "user", "content": msg}

    def _user_msg_with_imgs(self, msg: str, images: Optional[Union[str, list[str]]]):
        """
        images: can be list of http(s) url or base64
        """
        if isinstance(images, str):
            images = [images]
        content = [{"type": "text", "text": msg}]
        for image in images:
            # image url or image base64
            url = image if image.startswith("http") else f"data:image/jpeg;base64,{image}"
            # it can with multiple-image inputs
            content.append({"type": "image_url", "image_url": {"url":url}})
        return {"role": "user", "content": content}

    def _assistant_msg(self, msg: str) -> dict[str, str]:
        return {"role": "assistant", "content": msg}

    def _system_msg(self, msg: str) -> dict[str, str]:
        return {"role": "system", "content": msg}

    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        return self._system_msg(self.system_prompt)

class ZhipuAILLM(LLMOnline):
    def __init__(self, model_name: str = "zhipu-ai/DialoGPT-medium"):
        super().__init__(model_name)

    def generate_response(self, prompt: str, history: list = None) -> str:
        # 调用Zhipu AI的API来生成回复
        response = self.call_api(prompt, history)
        return response
    
    
    
class OpenAILLM(LLMOnline):
    # def __init__(self) -> None:
    #     self._init_client()
    @model_validator(mode='after')
    def _init_client(self):
        kwargs = self._make_client_kwargs()
        self.aclient = AsyncOpenAI(**kwargs)
        
    def _make_client_kwargs(self) -> dict:
        print(self.api_key,self.base_url)
        kwargs = {"api_key": self.api_key, "base_url": self.base_url}

        # to use proxy, openai v1 needs http_client
        if proxy_params := self._get_proxy_params():
            kwargs["http_client"] = AsyncHttpxClientWrapper(**proxy_params)

        return kwargs

    def _get_proxy_params(self) -> dict:
        params = {}
        # if self.proxy:
        #     params = {"proxies": self.proxy}
        #     if self.base_url:
        #         params["base_url"] = self.base_url

        return params
    def _cons_kwargs(self, messages: list[dict], timeout=3, **extra_kwargs) -> dict:
        kwargs = {
            "messages": messages,
            # "max_tokens": self._get_max_tokens(messages),
            # "n": 1,  # Some services do not provide this parameter, such as mistral
            # "stop": None,  # default it's None and gpt4-v can't have this one
            "temperature": self.temperature,
            "model": self.model,
            "timeout": max(self.timeout, timeout),
        }
        if extra_kwargs:
            kwargs.update(extra_kwargs)
        return kwargs
    
    def get_choice_text(self, rsp: ChatCompletion) -> str:
        """Required to provide the first text of choice"""
        return rsp.choices[0].message.content if rsp.choices else ""
    
    async def generate_text(self,query:str,image:Optional[str] = None,timeout=3)->str:
        messages = self._user_msg(query,image)
        kwargs = self._cons_kwargs(messages, timeout)
        rsp:ChatCompletion = await self.aclient.chat.completions.create(**kwargs)
        return self.get_choice_text(rsp)
    
    async def generate_text_stream(self, query:str,image:Optional[str] = None,timeout=20):
        user_message = self._user_msg(query,image)
        sys_message = self._system_msg('you are a helpful assistant.')
    #     messages = [{'role':'system',"content":"You are a helpful assistant."},{'role':'user',"content":[
    #     {
    #         "type":"text","text":"what's in this image"
    #     },
    #             {
    #         "type":"image_url","image_url":{
    #             "url":"https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png"
    #         }
    #     }
    # ]}]
        messages = [sys_message,user_message]
        print('messages',messages)
        response: AsyncStream[ChatCompletionChunk] = await self.aclient.chat.completions.create(
            **self._cons_kwargs(messages, timeout=timeout), stream=True
        )
        usage = None
        collected_messages = []
        async for chunk in response:
            chunk_message = chunk.choices[0].delta.content or "" if chunk.choices else ""
            print('chunk_message',chunk_message)
            yield chunk_message
            # extract the message
        #     print(chunk_message)
        #     collected_messages.append(chunk_message)
        # full_reply_content = "".join(collected_messages)
        # return full_reply_content
         
          
    async def gen_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        model: str = None,
        resp_format: str = "url",
    ) -> list["Image"]:
        """image generate"""
        assert resp_format in ["url", "b64_json"]
        if not model:
            model = self.model
        res = await self.aclient.images.generate(
            model=model, prompt=prompt, size=size, quality=quality, n=1, response_format=resp_format
        )
        imgs = []
        for item in res.data:
            img_url_or_b64 = item.url if resp_format == "url" else item.b64_json
            imgs.append(decode_image(img_url_or_b64))
        return imgs
        
    
        
        