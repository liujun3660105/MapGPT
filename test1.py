from datasource.rdmbs.conn_postgresql import PostgreSQLDatabase
from config.config import Config
CFG = Config()

# db = PostgreSQLDatabase()
db = PostgreSQLDatabase.from_uri_db(host=CFG.LOCAL_DB_HOST,port = CFG.LOCAL_DB_PORT,user = CFG.LOCAL_DB_USER,pwd=CFG.LOCAL_DB_PASSWORD,db_name=CFG.LOCAL_DB_NAME)

def get_all_tables():
    """获取当前数据库的所有表名称和字段信息"""
    table_info_list=db.table_simple_info()
    result_str = "这是当前数据库中所有的表名称和表结构："
    for table in table_info_list:
        table_name = table[0]
        table_schema = table[1]#'id,name'
        result_str+=f'\n\n 表名称:{table_name}\n表字段:{table_schema}'
    return result_str

    
    
def get_example_data(table_name,example_length=3):
    """获取 数据库的前 n 行的表结构和数据"""
    result = ''
    
    fields = db.get_fields(table_name)
    fields_str = ' '.join(field[0] for field in fields)

    
    example_data = db.get_example_data(table_name,example_length)
    item_str_list = [] 
    for item in example_data:
        item_value_list = [str(item_value) for item_value in item]
        item_str = ' '.join(item_value_list)
        item_str_list.append(item_str)
    data_str = '\n'.join(item_str_list)
    schema_str = fields_str+'\n'+data_str
    result += f"这是 '{table_name}' 表第前{example_length}行样例：\n\n{schema_str}"
    return result

def execute_sql_search(sql):
    result = db.query_ex(sql,'all')
    return f'结果为{result[1]}'

def get_table_spatial_ref(table_name):
    result = db.query_ex(f'select st_srid(geom) from {table_name} limit 1','one')
    return f'{table_name}表的空间数据坐标系为{result[1][0]}'



sql_text = 'SELECT ST_AsGeoJSON(road.geom) FROM road_centerline road, village WHERE ST_DWithin(road.geom, village.geom, 500)'


result = execute_sql_search(sql_text)
print(result)