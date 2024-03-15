import warnings

from pydantic import Field

warnings.filterwarnings("ignore")
from langchain.agents import Tool
from langchain.tools import StructuredTool
from .FileQATool import ask_docment
from .WriterTool import writer_chain
from .EmailTool import send_email
from .ExcelTool import get_first_n_rows, get_column_names
# from .DataBaseTool import get_all_tables,get_example_data



document_qa_tool = StructuredTool.from_function(
    func=ask_docment,
    name="AskDocument",
    description="根据一个Word或PDF文档的内容，回答一个问题。考虑上下文信息，确保问题对相关概念的定义表述完整。",
)

document_generation_tool = Tool.from_function(
    func=writer_chain.run,  # 可以用其它chain的run方法
    name="GenerateDocument",
    description="根据需求描述生成一篇正式文档",
)

email_tool = StructuredTool.from_function(
    func=send_email,
    name="SendEmail",
    description="给指定的邮箱发送邮件。确保邮箱地址是xxx@xxx.xxx的格式。多个邮箱地址以';'分割。",
)

excel_inspection_tool = StructuredTool.from_function(
    func=get_first_n_rows,
    name="InspectExcel",
    description="探查表格文件的内容和结构，展示它的列名和前n行，n默认为3",
)

# database_table_choose_tool = StructuredTool.from_function(
#     func=get_all_tables,
#     name="InspectDataBaseTable",
#     description="探查数据库中的所有表，展示它的表明和表的字段",
# )

# database_inspection_tool = StructuredTool.from_function(
#     func=get_example_data,
#     name="InspectDataBase",
#     description="探查数据库中某个表的内容和结构，展示它的列名和前n行，n默认为3",
# )

