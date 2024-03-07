# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from MapAgent.MapGPT import MapGPT
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from Tools import *
from Tools.PythonTool import ExcelAnalyser
from Tools.SqlTool import SqlAnalyser
from langchain.agents.agent_toolkits import FileManagementToolkit


def launch_agent(agent: MapGPT):
    human_icon = "\U0001F468"
    ai_icon = "\U0001F916"

    while True:
        task = input(f"{ai_icon}：有什么可以帮您？\n{human_icon}：")
        if task.strip().lower() == "quit":
            break
        reply = agent.run(task, verbose=True)
        print(f"{ai_icon}：{reply}\n")


def main():

    # 语言模型
    llm = ChatOpenAI(
        model="gpt-4-1106-preview",
        temperature=0,
        model_kwargs={
            "seed": 42
        },
    )

    # 存储长时记忆的向量数据库
    db = Chroma.from_documents([Document(page_content="")], OpenAIEmbeddings(model="text-embedding-ada-002"))
    retriever = db.as_retriever(search_kwargs=dict(k=1))

    # 自定义工具集
    tools = [
        document_qa_tool,
        document_generation_tool,
        email_tool,
        excel_inspection_tool,
        database_table_choose_tool,
        database_inspection_tool
    ]

    # 添加文件管理工具
    tools += FileManagementToolkit(
        root_dir="."
    ).get_tools()

    # 添加Excel分析工具
    tools += [ExcelAnalyser(
        prompts_path="./prompts/tools",
        prompt_file="excel_analyser.json"
    ).as_tool(),SqlAnalyser(prompts_path='./prompts/tools',prompt_file="database_analyser.json").as_tool()]

    # 定义智能体
    agent = MapGPT(
        llm=llm,
        prompts_path="./prompts/main",
        tools=tools,
        # work_dir="./data",
        main_prompt_file="main.json",
        final_prompt_file="final_step.json",
        max_thought_steps=20,
        memery_retriever=retriever
    )

    # 运行智能体
    launch_agent(agent)


if __name__ == "__main__":
    main()
