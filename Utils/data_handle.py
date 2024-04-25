import re
import json
import os
import time

def json_to_markdown(data, level=1):
    """
    将目录转换成markdown源码
    """
    markdown = ""
    for item in data:
        if type(item) is str:
            title = item
        else:
            title = item.get("title")
        if title:
            markdown += "#" * level + " " + title + "\n"
        sub_directory =item.get("directory") if type(item) is not str else None
        if sub_directory:
            if not isinstance(sub_directory, list):
                sub_directory = [sub_directory]
            else:
                markdown += json_to_markdown(sub_directory, level + 1)
    return markdown


def find_leaf_nodes(directory)->list:
    """寻找叶子节点"""
    leaf_nodes = []
    def traverse(node):
        if isinstance(node, dict) and 'directory' in node:
            for item in node['directory']:
                traverse(item)
        elif isinstance(node,
                        dict) and 'title' in node and 'directory' not in node:
            leaf_nodes.append(node['title'])
    for item in directory:
        traverse(item)
    return leaf_nodes


def insert_into_markdown(original_md, target_heading_text, new_content, heading_levels=["#", "##", "###", "####", "#####", "######"]):
    updated_md = original_md
    for hashes in heading_levels:
        pattern = rf'(?m)^({hashes} {target_heading_text})\n'
        match = re.search(pattern, original_md)
        if match:
            index = match.end()
            updated_md = original_md[:index] + new_content + original_md[index:]
            break
    return updated_md




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
    
    
def truncate_filename(filename, max_length=200):
    # 获取文件名后缀
    file_ext = os.path.splitext(filename)[1]

    # 获取不带后缀的文件名
    file_name_no_ext = os.path.splitext(filename)[0]

    # 计算文件名长度，注意中文字符
    filename_length = len(filename.encode('utf-8'))

    # 如果文件名长度超过最大长度限制
    if filename_length > max_length:
        # 生成一个时间戳标记
        timestamp = str(int(time.time()))
        # 截取文件名
        while filename_length > max_length:
            file_name_no_ext = file_name_no_ext[:-4]
            new_filename = file_name_no_ext + "_" + timestamp + file_ext
            filename_length = len(new_filename.encode('utf-8'))
    else:
        new_filename = filename

    return new_filename