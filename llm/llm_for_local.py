from llm.base import BaseLLM
from pydantic import BaseModel,model_validator
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from Utils.device import get_device

class ModelType(Enum):
    QwenVL="qwen_vl"
    QwenAudio="qwen_audio"
    

class LocalLLM(BaseLLM,ABC):
    model_path:str
    @abstractmethod
    def load(self,model_path:str,from_pretrained_kwargs:dict):
        pass

class QwenChatLLM(LocalLLM):
    model:Any=None
    tokenizer:Any=None
    from_pretrained_kwargs:dict = {}
    @model_validator(mode='after')
    def load(self):
        try:
            import transformers
            from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package "
                "Please install it with `pip install transformers`."
            ) from exc
        self.check_dependencies()

        revision = self.from_pretrained_kwargs.get("revision", "main")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast = False,
                # use_fast=self.use_fast_tokenizer(),
                # revision=revision,
                trust_remote_code=True,
            )
        except TypeError:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, use_fast=False, revision=revision, trust_remote_code=True
            )
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path, low_cpu_mem_usage=True, **self.from_pretrained_kwargs,trust_remote_code=True
            )
        except NameError:
            self.model = AutoModel.from_pretrained(
                self.model_path, low_cpu_mem_usage=True, **self.from_pretrained_kwargs,trust_remote_code=True
            )
    def check_dependencies(self) -> None:
        """Check if the dependencies are installed

        Raises:
            ValueError: If the dependencies are not installed
        """
        try:
            import transformers
        except ImportError as exc:
            raise ValueError(
                "Could not import depend s python package "
                "Please install it with `pip install transformers`."
            ) from exc
        self.check_transformer_version(transformers.__version__)

    def check_transformer_version(self, current_version: str) -> None:
        if not current_version >= "4.34.0":
            raise ValueError(
                "Current model (Load by NewHFChatModelAdapter) require transformers.__version__>=4.34.0"
            )
    def generate_text_stream(self, prompt,history=None):
        position = 0
        result = []
        try:
            for response in self.model.chat_stream(self.tokenizer,prompt,history):
                result.append(response[position:])
                position = len(response)
                yield "".join(result)
        except Exception as e:
            raise ValueError(f"model output has error {e}")
    def generate_text(self, prompt):
        try:
            inputs = self.tokenizer(prompt,return_tensors="pt")
            pred = self.model.generate(**inputs)
            return self.model.deocde()
        except Exception as e:
            raise ValueError(f"model output has error {e}")
    

        
class QwenVLAndAudioChatLLM(LocalLLM):
    model:Any=None
    tokenizer:Any=None
    from_pretrained_kwargs:dict = {}
    type:ModelType
    @model_validator(mode='after')
    def load(self):
        try:
            import transformers
            from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer
            from transformers.generation import GenerationConfig
        except ImportError as exc:
            raise ValueError(
                "Could not import depend python package "
                "Please install it with `pip install transformers`."
            ) from exc
        self.check_dependencies()

        revision = self.from_pretrained_kwargs.get("revision", "main")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                use_fast = False,
                # use_fast=self.use_fast_tokenizer(),
                # revision=revision,
                trust_remote_code=True,
            )
        except TypeError:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, use_fast=False, revision=revision, trust_remote_code=True
            )
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path, low_cpu_mem_usage=True, **self.from_pretrained_kwargs,trust_remote_code=True,device_map=get_device()
            ).eval()
            self.model.generation_config = GenerationConfig.from_pretrained(self.model_path, trust_remote_code=True)

        except NameError:
            self.model = AutoModel.from_pretrained(
                self.model_path, low_cpu_mem_usage=True, **self.from_pretrained_kwargs,trust_remote_code=True
            )
    def check_dependencies(self) -> None:
        """Check if the dependencies are installed

        Raises:
            ValueError: If the dependencies are not installed
        """
        try:
            import transformers
        except ImportError as exc:
            raise ValueError(
                "Could not import depend s python package "
                "Please install it with `pip install transformers`."
            ) from exc
        self.check_transformer_version(transformers.__version__)

    def check_transformer_version(self, current_version: str) -> None:
        if not current_version >= "4.34.0":
            raise ValueError(
                "Current model (Load by NewHFChatModelAdapter) require transformers.__version__>=4.34.0"
            )
    def generate_text_stream(self, query,fileUrl,history=None):
        position = 0
        result = []
        prompt = self._prepare_prompt(query,fileUrl)
        try:
            for response in self.model.chat_stream(self.tokenizer,prompt,history):
                print('response',response)
                result.append(response[position:])
                position = len(response)
                yield "".join(result)
        except Exception as e:
            raise ValueError(f"model output has error {e}")
    def generate_text(self, query,fileUrl=None,history=None):
        prompt = self._prepare_prompt(query,fileUrl)
        try:
            response, history = self.model.chat(self.tokenizer, query=prompt, history=None)
            print('response0',response)
            return response
        except Exception as e:
            raise ValueError(f"model output has error {e}")
    def _prepare_prompt(self,query,fileUrl):
        if fileUrl is None:
            prompt= query
        else:
            if ModelType==ModelType.QwenAudio:
                prompt = self.tokenizer.from_list_format([
                {"image":fileUrl},{"text":query}
            ])
            else:
                prompt = self.tokenizer.from_list_format([
            {"audio":fileUrl},{"text":query}
        ])
        return prompt
class Vllm(LocalLLM):
    def load(self, model_path: str, from_pretrained_kwargs: dict):
        pass
    def generate_text(self, prompt):
        pass
    @model_validator(mode='after')
    def llmLoader(self):
        print('load',self.model_path,self.model_type)
    
    
    
