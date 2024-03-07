import re
import os
from langchain.tools import StructuredTool
from Utils.PromptTemplateBuilder import PromptTemplateBuilder
from Utils.PythonExecUtil import execute_python_code
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from .ExcelTool import get_first_n_rows, get_column_names
from .DataBaseTool import execute_sql_search,get_example_data,get_table_spatial_ref

class SqlAnalyser:

    def __init__(self, prompts_path, prompt_file="database_analyser.json"):
        self.prompt = PromptTemplateBuilder(prompts_path, prompt_file).build()

    def analyse(self, query,table_name):

        """分析一个数据库表的内容。"""

        #columns = get_column_names(filename)
        inspections = get_example_data(table_name, 3)
        spatial_ref = get_table_spatial_ref(table_name)

        chain = LLMChain(
            llm=ChatOpenAI(
                # openai_api_key = os.environ('OPENAI_API_KEY'),
                # openai_api_base = os.environ('OPENAI_API_BASE'),
                model="gpt-4-1106-preview",
                temperature=0,
                model_kwargs={
                    "seed": 42,
                },
            ),
            prompt=self.prompt
        )
        response = chain.run(
            query=query,
            table_name=table_name,
            inspections=inspections,
            spatial_ref = spatial_ref
        )

        #print("\n"+response+"\n")

        code = self._extract_sql_code(response)

        if code:
            ans = execute_sql_search(code)
            return ans
        else:
            return "没有找到可执行的SQL代码"

    def _remove_marked_lines(self, input_str: str) -> str:
        lines = input_str.strip().split('\n')
        if lines and lines[0].strip().startswith('```'):
            del lines[0]
        if lines and lines[-1].strip().startswith('```'):
            del lines[-1]

        ans = '\n'.join(lines)
        return ans

    def _extract_sql_code(self, text: str) -> str:
        # 使用正则表达式找到所有的Python代码块
        sql_code_blocks = re.findall(r'```sql\n(.*?)\n```', text, re.DOTALL)
        # 从re返回结果提取出Python代码文本
        sql_code = None
        if len(sql_code_blocks) > 0:
            sql_code = sql_code_blocks[0]
            sql_code = self._remove_marked_lines(sql_code)
        return sql_code

    def as_tool(self):
        return StructuredTool.from_function(
            func=self.analyse,
            name="DatabaseQueryAnalysis",
            description="通过程序脚本分析一个数据库表的内容。输人中必须包含要分析的表名称和具体分析方式和分析依据，阈值常量等。如果输入信息不完整，你可以拒绝回答。",
        )

if __name__ == "__main__":
    print(SqlAnalyser(
        prompts_path="../prompts/tools"
    ).analyse(
        query="统计一下次干道长度",
        tablename="road_centerline"
    ))