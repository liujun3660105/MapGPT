from llm.llm_for_local import QwenVLAndAudioChatLLM,ModelType

model = QwenVLAndAudioChatLLM(model_path='/Users/liujun/learing/AI/self-deployment/model/VL/Qwen-VL-Chat')
# response = model.generate_text_stream(query='这是什么',image='https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg')
# for r in response:
#     print(r)
    
    
response = model.generate_text(query='这是什么',image='https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg')
print('response1',response)

# model = Hf(model_path='/Users/liujun/learing/AI/self-deployment/model/Qwen/Qwen-1_8B-chat',model_type=ModelType.QwenAudio)

# response = model.generate_text_stream('给我讲一个笑话')
# for r in response:
#     print(r)

