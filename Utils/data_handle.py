import re
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