import re
from langchain.tools import StructuredTool
from Utils.PromptTemplateBuilder import PromptTemplateBuilder
from Utils.PythonExecUtil import execute_python_code
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from .ExcelTool import get_first_n_rows, get_column_names


class ExcelAnalyser:

    def __init__(self, prompts_path, prompt_file="excel_analyser.json"):
        self.prompt = PromptTemplateBuilder(prompts_path, prompt_file).build()

    def analyse(self, query, filename):

        """分析一个结构化文件（例如excel文件）的内容。"""

        #columns = get_column_names(filename)
        inspections = get_first_n_rows(filename, 3)

        chain = LLMChain(
            llm=ChatOpenAI(
                model="gpt-4-1106-preview",
                temperature=0,
                model_kwargs={
                    "seed": 42
                },
            ),
            prompt=self.prompt
        )
        response = chain.run(
            query=query,
            filename=filename,
            inspections=inspections
        )

        #print("\n"+response+"\n")

        code = self._extract_python_code(response)

        if code:
            ans = execute_python_code(code)
            return ans
        else:
            return "没有找到可执行的Python代码"

    def _remove_marked_lines(self, input_str: str) -> str:
        lines = input_str.strip().split('\n')
        if lines and lines[0].strip().startswith('```'):
            del lines[0]
        if lines and lines[-1].strip().startswith('```'):
            del lines[-1]

        ans = '\n'.join(lines)
        return ans

    def _extract_python_code(self, text: str) -> str:
        # 使用正则表达式找到所有的Python代码块
        python_code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        # 从re返回结果提取出Python代码文本
        python_code = None
        if len(python_code_blocks) > 0:
            python_code = python_code_blocks[0]
            python_code = self._remove_marked_lines(python_code)
        return python_code

    def as_tool(self):
        return StructuredTool.from_function(
            func=self.analyse,
            name="AnalyseExcel",
            description="通过程序脚本分析一个结构化文件（例如excel文件）的内容。输人中必须包含文件的完整路径和具体分析方式和分析依据，阈值常量等。如果输入信息不完整，你可以拒绝回答。",
        )

if __name__ == "__main__":
    print(ExcelAnalyser(
        prompts_path="../prompts"
    ).analyse(
        query="8月销售额",
        filename="../data/2023年8月-9月销售记录.xlsx"
    ))