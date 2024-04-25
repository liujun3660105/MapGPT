from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    generate_from_stream,
)

from langchain_core.outputs import ChatGeneration, ChatGenerationChunk,GenerationChunk,ChatResult
from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

# common types
from typing import Type, Any, Mapping, Dict, Iterator, List, Optional, cast, Union,AbstractSet,Collection

# async
import asyncio
from typing import AsyncIterator,Literal

# all message types
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    ToolMessage,
    ToolMessageChunk,
    FunctionMessage,
    FunctionMessageChunk,
    SystemMessage,
    SystemMessageChunk,
    ChatMessage,
    ChatMessageChunk,
)

from http import HTTPStatus
import tiktoken

def _convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    """Convert a dictionary to a LangChain message.

    Args:
        _dict: The dictionary.

    Returns:
        The LangChain message.
    """
    role = _dict.get("role")
    if role == "user":
        return HumanMessage(content=_dict.get("content", ""))
    elif role == "assistant":
        content = _dict.get("content", "") or ""
        additional_kwargs: Dict = {}
        if tool_calls := _dict.get("tool_calls"):
            additional_kwargs["tool_calls"] = tool_calls
        return AIMessage(content=content, additional_kwargs=additional_kwargs)
    elif role == "system":
        return SystemMessage(content=_dict.get("content", ""))
    elif role == "tool":
        additional_kwargs = {}
        return ToolMessage(
            content=_dict.get("content", ""),
            tool_call_id=_dict.get("tool_call_id"),
            additional_kwargs=additional_kwargs,
        )
    else:
        return ChatMessage(content=_dict.get("content", ""), role=role)

def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    message_dict: Dict[str, Any]
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if "tool_calls" in message.additional_kwargs:
            message_dict["tool_calls"] = message.additional_kwargs["tool_calls"]
            # If tool calls only, content is None not empty string
            if message_dict["content"] == "":
                message_dict["content"] = None
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, ToolMessage):
        message_dict = {
            "role": "tool",
            "content": message.content,
            "tool_call_id": message.tool_call_id,
        }
    else:
        raise TypeError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]
    return message_dict

def _convert_delta_to_message_chunk(
    _dict: Mapping[str, Any], default_class: Type[BaseMessageChunk]
) -> BaseMessageChunk:
    role = cast(str, _dict.get("role"))
    content = cast(str, _dict.get("content") or "")
    additional_kwargs: Dict = {}
    if _dict.get("tool_calls"):
        additional_kwargs["tool_calls"] = _dict["tool_calls"]

    if role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=content)
    elif role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(content=content, additional_kwargs=additional_kwargs)
    elif role == "system" or default_class == SystemMessageChunk:
        return SystemMessageChunk(content=content)
    elif role == "tool" or default_class == ToolMessageChunk:
        return ToolMessageChunk(content=content, tool_call_id=_dict["tool_call_id"])
    elif role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=content, role=role)
    else:
        return default_class(content=content)  # type: ignore

class ChatDashScope(BaseChatModel):
    """支持最新的阿里云服务模型灵积的API"""

    @property
    def lc_secrets(self) -> Dict[str, str]:
        return {"dash_scope_api_key": "DASHSCOPE_API_KEY"}

    @property
    def _llm_type(self) -> str:
        """Return the type of chat model."""
        return "tongyi_qw"

    @property
    def lc_attributes(self) -> Dict[str, Any]:
        attributes: Dict[str, Any] = {}

        if self.model:
            attributes["model"] = self.model

        if self.streaming:
            attributes["streaming"] = self.streaming

        if self.return_type:
            attributes["return_type"] = self.return_type

        return attributes

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "chat_models", "ZhipuAI"]
    
    client: Any = None
    """访问DashScope的客户端"""
    
    api_key: str = None

    model: str = Field(default="qwen-plus")
    """指定用于对话的通义千问模型名，目前可选择：
    - qwen-turbo
    - qwen-plus
    - qwen-max
    - qwen-max-longcontext
    - bailian-v1
    - dolly-12b-v2
    - ... 还有更多，请查阅官方文档
    """
    streaming:bool = Field(default=False)

    seed: Optional[int] = 1234
    """
    生成时使用的随机数种子，用户控制模型生成内容的随机性。
    seed支持无符号64位整数，默认值为1234。
    在使用seed时，模型将尽可能生成相同或相似的结果，但目前不保证每次生成的结果完全相同。
    """
    
    max_tokens: Optional[int] = 1500
    """用于指定模型在生成内容时token的最大数量，它定义了生成的上限，但不保证每次都会生成到这个数量。

    - qwen-turbo最大值和默认值为1500 tokens。
    - qwen-max、qwen-max-1201、qwen-max-longcontext和qwen-plus模型，最大值和默认值均为2000 tokens。
    """

    top_p: Optional[float] = None
    """
    生成过程中核采样方法概率阈值。
    例如，取值为0.8时，仅保留概率加起来大于等于0.8的最可能token的最小集合作为候选集。
    取值范围为（0,1.0)，取值越大，生成的随机性越高；取值越低，生成的确定性越高。
    """

    top_k: Optional[int] = None
    """
    生成时，采样候选集的大小。
    例如，取值为50时，仅将单次生成中得分最高的50个token组成随机采样的候选集。
    取值越大，生成的随机性越高；取值越小，生成的确定性越高。
    默认不传递该参数，取值为None或当top_k大于100时，表示不启用top_k策略，此时，仅有top_p策略生效。
    """

    repetition_penalty: Optional[float] = 1.1
    """
    用于控制模型生成时的重复度。
    提高repetition_penalty时可以降低模型生成的重复度。
    1.0表示不做惩罚。
    """

    temperature: Optional[float] = 0.85
    """
    用于控制随机性和多样性的程度。
    具体来说，temperature值控制了生成文本时对每个候选词的概率分布进行平滑的程度。
    较高的temperature值会降低概率分布的峰值，使得更多的低概率词被选择，生成结果更加多样化；
    而较低的temperature值则会增强概率分布的峰值，使得高概率词更容易被选择，生成结果更加确定。

    取值范围： [0, 2)，不建议取值为0，无意义。
    """

    stop: Optional[Union[str, List[str], List[int], List[List[int]]]] = None
    """
    str/list[str]用于指定字符串；list[int]/list[list[int]]用于指定token_ids
    
    - stop参数用于实现内容生成过程的精确控制，在生成内容即将包含指定的字符串或token_ids时自动停止，生成内容不包含指定的内容。

    例如，如果指定stop为"你好"，表示将要生成"你好"时停止；如果指定stop为[37763, 367]，表示将要生成"Observation"时停止。

    - stop参数支持以list方式传入字符串数组或者token_ids数组，支持使用多个stop的场景。
    
    说明：list模式下不支持字符串和token_ids混用，list模式下元素类型要相同。
    """

    enable_search: Optional[bool] = False
    """
    模型内置了互联网搜索服务，该参数控制模型在生成文本时是否参考使用互联网搜索结果。
    
    取值如下：

    - True：启用互联网搜索，模型会将搜索结果作为文本生成过程中的参考信息，但模型会基于其内部逻辑“自行判断”是否使用互联网搜索结果。
    - False（默认）：关闭互联网搜索。
    """

    allowed_special: Union[Literal["all"], AbstractSet[str]] = set()
    """Set of special tokens that are allowed。"""

    disallowed_special: Union[Literal["all"], Collection[str]] = "all"
    """Set of special tokens that are not allowed。"""


    @classmethod
    def filter_model_kwargs(cls):
        """
        通义千问在调用时只接受这些参数。
        """
        return [
            "model",
            "api_key",
            "seed",
            "max_tokens",
            "top_p",
            "top_k",
            "repetition_penalty",
            "temperature",
            "stop",
            "enable_search",
            "streaming"
        ]

    # 获得模型调用参数
    def get_model_kwargs(self):
        params = {}
        for attr, value in self.__dict__.items():
            if attr in self.__class__.filter_model_kwargs() and value is not None:
                params[attr] = value
        return params

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        try:
            import dashscope
            values["client"] =  dashscope.Generation
        except ImportError:
            raise RuntimeError(
                "Could not import dashscope package. "
                "Please install it via 'pip install -U dashscope'"
            )
        return values

    # 实现 invoke 调用方法
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """实现 DashScope 的同步调用"""
        prompt = [_convert_message_to_dict(message) for message in messages]

        # 构造参数序列
        params = self.get_model_kwargs()
        params.update(kwargs)
        params.update({"stream": self.streaming})
        params.update({"result_format": "message"})
   
        if stop is not None:
            params.update({"stop": stop})
        generations = []
        # 调用模型

        if self.streaming:
            gen:Optional[ChatGenerationChunk] = None
            for chunk in self._stream(messages,stop,run_manager,params):
                if gen is None:
                    gen = chunk
                else:
                    gen+=chunk
            generations.append(gen)
            
        else:
            response = self.client.call(
            messages=prompt,
            **params
        )
        
        # 异常处理
        if response.status_code != HTTPStatus.OK:
            raise Exception('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))

        if not isinstance(response, dict):
            response = response.dict()
        output = response["output"] if "output" in response and isinstance(response["output"], dict) else {}
        generation_info = dict(finish_reason=output.get("finish_reason"))

        
        for res in output["choices"]:
            message = _convert_dict_to_message(res["message"])
            gen = ChatGeneration(
                message=message,
                generation_info=generation_info,
            )
            generations.append(gen)
        llm_output = {
            "request_id": response.get("request_id"),
            "created": response.get("created"),
            "token_usage": response.get("usage", {}),
            "model_name": self.model,
        }
        return ChatResult(generations=generations, llm_output=llm_output)

    # 实现 stream 调用方法
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """实现 DashScope 的事件流调用"""
        prompt = [_convert_message_to_dict(message) for message in messages]

        # 构造参数序列
        params = self.get_model_kwargs()
        params.update(kwargs)
        params.update({"result_format": "message"})
        # 在流模式中，永远使用增量模式
        params.update({"stream": True})
        params.update({"incremental_output": True})
        if stop is not None:
            params.update({"stop": stop})
    
        # 调用模型
        responses = self.client.call(
            messages=prompt,
            **params
        )
        
        for response in responses:
            # 异常处理
            if response.status_code != HTTPStatus.OK:
                raise Exception('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                    response.request_id, response.status_code,
                    response.code, response.message
                ))

            if not isinstance(response, dict):
                response = response.dict()
            output = response["output"] if "output" in response and isinstance(response["output"], dict) else {}

            default_chunk_class = AIMessageChunk
            if not isinstance(output, dict):
                output = output.dict()
            if len(output["choices"]) == 0:
                continue
            choice = output["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["message"], default_chunk_class
            )
            generation_info = {}
            if finish_reason := choice.get("finish_reason"):
                generation_info["finish_reason"] = finish_reason
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(
                message=chunk, generation_info=generation_info or None
            )
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """实现 DashScope 的事件流调用"""
        prompt = [_convert_message_to_dict(message) for message in messages]

        # 构造参数序列
        params = self.get_model_kwargs()
        params.update(kwargs)
        params.update({"result_format": "message"})
        # 在流模式中，永远使用增量模式
        params.update({"stream": True})
        params.update({"incremental_output": True})
        if stop is not None:
            params.update({"stop": stop})

        # 创建用于异步调用的函数
        def create_completions():
            return self.client.call(
                messages=prompt,
                **params
            )

        # 使用asyncio构建异步调用
        loop = asyncio.get_running_loop()
        responses = await loop.run_in_executor(None, create_completions)

        for response in responses:
            if not isinstance(response, dict):
                response = response.dict()
            output = response["output"] if "output" in response and isinstance(response["output"], dict) else {}

            default_chunk_class = AIMessageChunk
            if not isinstance(output, dict):
                output = output.dict()
            if len(output["choices"]) == 0:
                continue
            choice = output["choices"][0]
            chunk = _convert_delta_to_message_chunk(
                choice["message"], default_chunk_class
            )
            generation_info = {}
            if finish_reason := choice.get("finish_reason"):
                generation_info["finish_reason"] = finish_reason
            default_chunk_class = chunk.__class__
            chunk = ChatGenerationChunk(
                message=chunk, generation_info=generation_info or None
            )
            if run_manager:
                await run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    def get_token_ids(self, text: str) -> List[int]:
        """Get the token IDs using the tiktoken package."""

        encoding_model = tiktoken.get_encoding("cl100k_base")
        return encoding_model.encode(
            text,
            allowed_special=self.allowed_special,
            disallowed_special=self.disallowed_special,
        )