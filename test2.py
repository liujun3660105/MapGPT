from llm.llm_for_online import OpenAILLM
import os
import asyncio


async def main():

    llm = OpenAILLM(api_key=os.getenv('OPENAI_API_KEY'),base_url = os.getenv('OPENAI_API_BASE'),model='gpt-4o')
    async for rsp in llm.generate_text_stream(query='这张图片描述的是什么',image="https://zos.alipayobjects.com/rmsportal/jkjgkEfvpUPVyRjUImniVslZfWPnJuuZ.png"):
        print('rsp',rsp)
    
    
asyncio.run(main())