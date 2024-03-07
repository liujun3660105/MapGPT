# from contextlib import contextmanager
# class MyNewClass(object):
#     #执行with语句时，先执行 __enter__方法，并将返回值复制给 with 后的变量，比如new_class
#     def __enter__(self):
#         print("Before exect my_function.")
#         return self

#     # with语句执行完成后，执行 __exit__ 方法，进行收尾、善后（异常处理）等工作，注意*args接收三个参数（exc_type, exc_val, exc_tb）
#     # exc_type ：若无异常则为 None; 若有异常则为异常类型。
#     # exc_val ：若无异常则为 None, 若有异常则为异常信息描述。
#     # exc_tb ：若无异常则为 None, 若有异常则为异常详细追溯信息（TraceBack）。
#     def __exit__(self, *args):
#         print("After exect my_function.",args)

#     def my_function(self):
#         print("Exect my_function.")


# # with MyNewClass() as new_class:
# #     new_class.my_function()
# #     x = 1/0

# @contextmanager
# def test_new_contextmanager():
#     print("Before exect my_function.")  # yield前内容等同于__enter__
#     yield  11# 需要执行的方法比如后面的 print("After exect my_function.")
#     print("Exect my_function.")  # yield前内容等同于__enter__


# with test_new_contextmanager() as new_contextmanager:
#     print("After exect my_function.")
#     a = new_contextmanager
#     print(a)

# a = test_new_contextmanager()
# print(a)

# from typing import Type, List
# class A:
#     id:int = 0
#     def __init__(self):
#         self.id = id
# class B(A):
#     name:str='tonttong'

# class C(A):
#     name:str='jiangyoumei'
    

# def get_all_subclasses(cls: Type[A]) -> List[Type[A]]:
#     subclasses = cls.__subclasses__()
#     for subclass in subclasses:
#         subclasses += get_all_subclasses(subclass)
#     return subclasses

# a = get_all_subclasses(A)
# print(a)
# class ConnectManager:
#     """db connect manager"""

from datasource.rdmbs.conn_postgresql import PostgreSQLDatabase
from config.config import Config
CFG = Config()

from Tools import SqlTool

# db = PostgreSQLDatabase()
db = PostgreSQLDatabase.from_uri_db(host=CFG.LOCAL_DB_HOST,port = CFG.LOCAL_DB_PORT,user = CFG.LOCAL_DB_USER,pwd=CFG.LOCAL_DB_PASSWORD,db_name=CFG.LOCAL_DB_NAME)


def get_table_spatial_ref(table_name):
    result = db.query_ex(f'select st_srid(geom) from {table_name} limit 1','one')
    result1 = f'{table_name}表的空间数据坐标系为{result[1][0]}'
    return result1

get_table_spatial_ref('road_centerline')
# def get_all_tables():
#     """获取当前数据库的所有表名称和字段信息"""
#     table_info_list=db.table_simple_info()
#     result_str = "这是当前数据库中所有的表名称和表结构："
#     for table in table_info_list:
#         table_name = table[0]
#         table_schema = table[1]#'id,name'
#         result_str+=f'\n\n 表名称:{table_name}\n表字段:{table_schema}'
#     return result_str


# def get_example_data(table_name):
#     """获取 数据库的前 3 行的表结构和数据"""
#     result = ''
    
#     fields = db.get_fields(table_name)
#     fields_str = ' '.join(field[0] for field in fields)

    
#     example_data = db.get_example_data(table_name,3)
#     item_str_list = []
#     for item in example_data:
#         item_value_list = [str(item_value) for item_value in item]
#         item_str = ' '.join(item_value_list)
#         item_str_list.append(item_str)
#     data_str = '\n'.join(item_str_list)
#     schema_str = fields_str+'\n'+data_str
#     result += f"这是 '{table_name}' 表第前{3}行样例：\n\n{schema_str}"

# def get_tabale_fields(table_name:str):
#     return db.get_simple_fields(table_name)
    

# aa = get_all_tables()
# print(aa)
# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv())


# # if __name__ == "__main__":
# print(SqlTool(
#     prompts_path="prompts/tools"
# ).analyse(
#     query="统计一下次干道长度",
#     tablename="road_centerline"
# ))