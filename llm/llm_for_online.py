from llm.base import LLM

class ZhipuAILLM(LLM):
    def __init__(self, model_name: str = "zhipu-ai/DialoGPT-medium"):
        super().__init__(model_name)

    def generate_response(self, prompt: str, history: list = None) -> str:
        # 调用Zhipu AI的API来生成回复
        response = self.call_api(prompt, history)
        return response