import json

aa = """[({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [117.668638395751, 39.0180067967628]}, 'properties': None}]},)]"""

def extract_potential_geojson(input_string:str):
    # 找到第一个 "{" 和最后一个 "}"
    start_brace_index = input_string.index('{')
    end_brace_index = input_string.rindex('}')
    # 提取出疑似GeoJSON对象的字符串
    potential_geojson_str = input_string[start_brace_index:end_brace_index + 1]
    # 尝试将字符串解析为字典
    try:
        potential_geojson_str = potential_geojson_str.replace("'","\"").replace('None','\"\"')
        potential_geojson_dict = json.loads(potential_geojson_str)
    except json.JSONDecodeError as e:
        print('error',e)
        return None
    # 检查类型是否为"Feature"或"FeatureCollection"
    if ('type' in potential_geojson_dict and 
        potential_geojson_dict['type'] in ['Feature', 'FeatureCollection']):
        return potential_geojson_dict
    else:
        return None
    
extract_potential_geojson(aa)