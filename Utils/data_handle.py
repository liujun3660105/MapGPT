import re
def json_to_markdown(data, level=1):
    """
    将目录转换成markdown源码
    """
    markdown = ""
    for item in data:
        title = item.get("title")
        if title:
            markdown += "#" * level + " " + title + "\n"
        sub_directory = item.get("directory")
        if isinstance(sub_directory, list) and not isinstance(
                sub_directory[0], dict):  # 如果子目录是字符串列表
            markdown += '\n'.join(
                ["#" * (level + 1) + " " + s for s in sub_directory]) + "\n"
        elif sub_directory:
            markdown += json_to_markdown(sub_directory, level + 1)
    return markdown



def find_leaf_nodes(directory):
    leaf_nodes = []
    def traverse(node):
        if isinstance(node, dict) and 'directory' in node:
            traverse(node['directory'])
        elif isinstance(node, list):
            for item in node:
                traverse(item)
        else:
            leaf_nodes.append(node)
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