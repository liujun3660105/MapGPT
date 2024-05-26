from llm.llm_for_local import QwenVLAndAudioChatLLM,ModelType
from .prompt import Query
class AudioCheck:
    def __init__(self):
        self.llm = QwenVLAndAudioChatLLM(model_path='/Users/liujun/learing/AI/self-deployment/model/VL/Qwen-VL-Chat',type=ModelType.QwenAudio)
    
    def check(self, audio_url,query):
        # 实现语音检查逻辑
        answer = self.llm.generate_text(query=query,fileUrl=audio_url)
        return answer