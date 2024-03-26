from typing import Dict
from metagpt.actions import Action
from metagpt.schema import Message
# from metagpt.prompts.tutorial_assistant import CONTENT_PROMPT, DIRECTORY_PROMPT
from metagpt.utils.common import OutputParser
from .prompt import SQL_GENERATOR,DATABASE_ANALYSIS,SUMMARIZE_ROLE
from Tools.DataBaseTool import get_all_tables,get_example_data,execute_sql_search_json,get_table_spatial_ref,execute_rollback
import re
from Tools.SqlTool import SqlAnalyser




class GetTableNameAndField(Action):
    """Action class for get related tableName by analyis database schema and example data.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    name: str = "GetTableNameAndField"
    language: str = "Chinese"
    desc: str = "Get related tableName and schema field by analyis database schema"
    directory:str=""

    async def run(self, demand: str,msg:str) -> Dict:
        """Execute the action to connect to database and get database info.

        Args:
            demand: The database config.

        Returns:
            related table name and schema field
        """
        schema_info = get_all_tables()
        prompt = DATABASE_ANALYSIS.format(table_schema=schema_info,question = demand)
        return await self._aask(prompt=prompt)
  
class SqlGenerator(Action):
    """Action class for generate pg spatial database sql.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    name: str = "SqlGenerator"
    language: str = "Chinese"
    desc: str = "Get Sql statement based on schema and user requirements"
    directory:str=""
    max_retry_steps:int = 5
    sql_history:str = ''

    async def run(self, question: str,schema:str, *args, **kwargs) -> Dict:
        """Execute the action to connect to database and get database info.

        Args:
            demand: The database config.

        Returns:
            sql statement
        """
        # FIXME: 这里要通过查询获取，默认一个数据库里的所有表的坐标系相同 spatial_ref = get_table_spatial_ref()
        current_step = 0
        success = False
        spatial_ref = 'wgs84 地理坐标系'
        # spatial_ref = get_table_spatial_ref()

        
        while not success and current_step < self.max_retry_steps:
            current_step+=1
            try:
                prompt = SQL_GENERATOR.format(question=question,schema = schema,spatial_ref = spatial_ref,sql_history = self.sql_history)
                result = await self._aask(prompt=prompt)
                sql_code = SqlAnalyser(prompts_path="./prompts/tools")._extract_sql_code(result)
                execute_sql_search_json(sql_code)
                success=True
            except Exception as e:
                current_result = f"第{current_step}次执行结果为{sql_code},执行失败，错误信息为：{e.orig.pgerror}"
                self.sql_history = f"{self.sql_history}\n{current_result}"
                execute_rollback()
        if not success and current_step >= self.max_retry_steps:
            raise Exception("正确的sql语句生成失败")
        # result = """生成的sql语句为:\n"""+sql_code
        # return result
        return sql_code
        
        
    
class SqlExecutor(Action):
    """Action class for exectute sql and get result.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    name: str = "SqlExecutor"
    language: str = "Chinese"
    desc: str = "execute sql statement and get result"
    history:str = ''

    async def run(self, user_requirement:str, sql: str, *args, **kwargs) -> Dict:
        """Execute the action to connect to database and get database info.

        Args:
            demand: The database config.

        Returns:
            related table name and schema field
        """
        sql_code = SqlAnalyser(prompts_path="./prompts/tools")._extract_sql_code(sql)
        result = execute_sql_search_json(sql_code)
        return f"已经拿到最后的结果，结果为:{result}"
        

class ResultSummarizer(Action):
    """Action class for summarize the result.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    name: str = "ResultSummarizer"
    language: str = "Chinese"
    desc: str = "summarize the result based on the user requirement"
    history:str = ''

    async def run(self, query:str, result: str, *args, **kwargs) -> Dict:
        """Execute the action to connect to database and get database info.

        Args:
            demand: The database config.

        Returns:
            related table name and schema field
        """
        prompt = SUMMARIZE_ROLE.format(query = query,result = result,language = self.language)
        return await self._aask(prompt=prompt)