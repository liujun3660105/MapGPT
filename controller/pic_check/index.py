from llm.llm_for_local import QwenVLAndAudioChatLLM,ModelType
from .prompt import Query
class PicCheck:
    def __init__(self):
        self.llm = QwenVLAndAudioChatLLM(model_path='/Users/liujun/learing/AI/self-deployment/model/VL/Qwen-VL-Chat',type=ModelType.QwenVL)
    
    def check(self, operation_image_url,right_answer_image_url):
        # 实现图片检查逻辑
        prompt = Query.format(operation_image_url =operation_image_url,right_answer_image_url=right_answer_image_url )
        answer = self.llm.generate_text(prompt)
        print('answer:', answer)
        return answer