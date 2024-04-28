import pandas as pd
from langchain.schema import Document
from typing import Any, List

def table_converter(table:List[Any]):
    table_string = ''
    # 遍历表格的每一行
    for row_num in range(len(table)):
        row = table[row_num]
        # 从warp的文字删除线路断路器
        cleaned_row = [str(item).replace('\n', ' ') if item is not None and '\n' in str(item) else 'None' if item is None else str(item) for item in row]
        # 将表格转换为字符串，注意'|'、'\n'
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    # 删除最后一个换行符
    table_string = table_string[:-1]
    return table_string

class ExcelLoader():
    def __init__(self,file_path:str,split_row_count:int = 10) -> None:
        self.file_path = file_path
        self.split_row_count = split_row_count

    def load(self):
        document_list = []
        with pd.ExcelFile(self.file_path) as df:
            for sheet_name in df.sheet_names:
                sheet_data = pd.read_excel(df,sheet_name)
                header = sheet_data.columns.values
                content = sheet_data.values
                for i in range(0,len(content),self.split_row_count):
                    chunk_content = content[i:i+self.split_row_count]
                    chunk_table_list = list(chunk_content)
                    chunk_table_list.insert(0,header)
                    chunk_table_str = table_converter(chunk_table_list)
                    document = Document(page_content=chunk_table_str,metadata={"source":f"${self.file_path}-{sheet_name}","page":i}) 
                    document_list.append(document)
        return document_list