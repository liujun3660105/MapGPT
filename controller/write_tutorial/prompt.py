from enum import Enum

COMMON_OUTPUT_FORMAT_EXAMPLE = """
[
    {{
        "title": "1xxx",
        "directory": [
            {{
                "title": "1.1xxx",
                "directory": [
                    {{
                        "title": "1.1.1xxx"
                    }}
                ]
            }},
            {{
                "title": "1.2xxx",
                "directory": [
                    {{
                        "title": "1.2.1xxx"
                    }},
                    {{
                        "title": "1.2.3xxx"
                    }}
                ]
            }}
        ]
    }},
    {{
        "title": "2xxx",
        "directory": [
            {{
                "title": "2.1xxx",
                "directory": [
                    {{
                        "title": "2.1.1xxx"
                    }},
                    {{
                        "title": "2.1.2xxx"
                    }}
                ]
            }},
            {{
                "directory": {{
                    "title": "2.2:xxx",
                    "directory": [
                        {{
                            "title": "2.2.1xxx"
                        }},
                        {{
                            "title": "2.2.2xxx"
                        }}
                    ]
                }}
            }},
            {{
                "title": "2.3xxx",
                "directory": [
                    {{
                        "title": "2.3.1xxx",
                        "directory": [
                            {{
                                "title": "2.3.1.1xxx"
                            }},
                            {{
                                "title": "2.3.1.2xxx"
                            }}
                        ]
                    }},
                    {{
                        "title": "2.3.2xxx",
                        "directory": [
                            {{
                                "title": "2.3.2.1xxx"
                            }},
                            {{
                                "title": "2.3.2.2xxx"
                            }}
                        ]
                    }}
                ]
            }}
        ]
    }}
]
"""

EXAMPLE_CASE="""

No.1 example:
######
original content:
1 MySQL 安装与配置
1.1 安装MySQL
1.2 配置MySQL服务器
2 MySQL 基本概念
2.1 数据库与表
2.2 数据类型和表结构
3 SQL查询与数据操作
3.1 SQL查询语言

output content:
[
    {{
        "title":"1 MySQL 安装与配置"
        "directory":[
            {{"title":"1.1 安装MySQL"}},
            {{"title":"1.2 配置MySQL服务器"}},
        ]
    }},
    {{
        "title":"2 MySQL 基本概念"
        "directory":[
            {{"title":"2.1 数据库与表"}},
            {{"title":"2.2 数据类型和表结构"}},
        ]
    }},
    {{
        "title":"3 MySQL 基本概念"
        "directory":[
            {{"title":"3.1 SQL查询与数据操作"}},
        ]
    }}

]

No.2 example:
#######
original content:
1 MySQL 安装与配置
1.1 安装MySQL
1.2 配置MySQL服务器
1.2.1 用户名密码配置
1.2.2 节点配置

output content:
[
    {{
        "title":"1 MySQL 安装与配置"
        "directory":[
            {{"title":"1.1 安装MySQL"}},
            {{
                "title":"1.2 配置MySQL服务器",
                "directory":[
                    {{"title":"1.2.1 用户名密码配置"}},
                    {{"title":"1.2.2 节点配置"}}
                ]
            }},
        ]
    }}

]
"""



COMMON_TECHNICAL_PROMPT = """
You are now a seasoned technical professional in the field of the internet. 
We need you to write a technical tutorial with the demand "{demand}".
"""
# COMMON_CONSTRUCTION_PROMPT = """
# You are now a seasoned solution professional in the field of the Enterprise information construction. 
# We need you to write a Enterprise Information building solutions with the background information for this informatization project "{demand}".
# """


COMMON_CONSTRUCTION_PROMPT = """
你是一名经验丰富的信息化系统解决方案专家，现在需要你结合提供给你的项目背景信息、总体目录结构和当前需要编写的小节标题，输出当前小节的建设内容。具体需求如下:"{demand}"
"""
# COMMON_CONSTRUCTION_PROMPT = """
# 你是一名经验丰富的信息化系统解决方案专家，现在需要你结合提供给你的项目背景信息、总体目录结构和当前需要编写的小节标题，输出当前小节的建设内容。具体需求如下:"{demand}"
# We need you to write a Enterprise Information building solutions with the background information for this informatization project "{demand}".
# """


## 技术文档目录生成，无自定义目录结构
TECHNICAL_DIRECTORY_PROMPT_WITHOUT_CUSTOM =  ("""You are now a seasoned technical professional in the field of the internet. 
We need you to write a technical tutorial with the demand "{demand}"."""
    + """
Please provide the specific table of contents for this tutorial, strictly following the following requirements:
1. The output must be strictly in the specified language, {language}.
2. Answer strictly in the dictionary format like:
"""+
COMMON_OUTPUT_FORMAT_EXAMPLE+
""".
3. The directory should be as specific and sufficient as possible, Each level of directory may contain multiple nested subdirectories.
4. Do not have extra spaces or line breaks.
5. Each directory title has practical significance.
6. leaf nodes only have 'title' key.
7.non-leaf nodes have the 'title' key and 'directory' key,and 'directory' key is an array contains the children. each element of the array is an object.
"""
)

## 技术文档目录生成，有自定义目录结构
TECHNICAL_DIRECTORY_PROMPT_WITH_CUSTOM = ("""Your goal is to transform the content  provided for you into another format"""+
    """
    The directory content provided for you is "{custom_directory}". Don't make assumptions, just turn the directory content I provided you into the required data format, strictly following the following requirements:
    """+
    """
1. The output must be strictly in the specified language, {language}.
2. Output strictly in the required dictionary format like: 
"""+COMMON_OUTPUT_FORMAT_EXAMPLE+
"""
.
3.Output the content strictly as the format provided for you,don't output other keys. 
4.You must consider the nested relationship of directory structures provided for you based on title number like '1', '1.1', '1.1.1', '2', '2.1'. And '1.1.1' and '2.1' are leaf nodes. Leaf nodes only have 'title' key and don't have 'directory' key.
5. Each level of directory may contain multiple nested subdirectories. When the leaf node object,it only contain 'title' key,no 'directory' key.
6. Do not have extra spaces or line breaks.
7.Fully understand the rules of the sample output directory format to ensure the right output format.
8. if the node key in the directory is 'directory',it must be an array.
9.Remembedr,Don't make any assumptions, just turn the directory content I provided you into the required data format.Even if I just provide you one title like ‘1 建设内容’,just turn it into [{{"title":"1 建设内容"}}]

examples:
"""+EXAMPLE_CASE
)



## 技术文档内容生成
TECHNICAL_CONTENT_PROMPT =("""
You are now a seasoned technical professional in the field of the internet. 
We need you to write a technical tutorial with the topic "{demand}".
"""+"""
Now I will give you the overall directory titles for the demand and the current section title. Please combine the overall directory structure to output the content of the current section.
Please output the detailed principle content of current section in detail. 
If there are code examples, please provide them according to standard code specifications. 

Without a code example, it is not necessary.

The module directory titles for the demand is as follows:
{directory}
The current section to be written as fowllow:
{current_section}

Strictly limit output according to the following requirements:
1. Follow the Markdown syntax format for layout.
2. If there are code examples, they must follow standard syntax specifications, have document annotations, and be displayed in code blocks.
3. The output must be strictly in the specified language, {language}.
4. Do not have redundant output, including concluding remarks.
5. Strict requirement not to output the demand "{demand}".
6. Only output the content of the current section, without including any other titles.
7. the output lenght is about {word_number} words
"""
)






## 建设方案目录生成，无自定义目录结构
CONSTRUCTION_DIRECTORY_PROMPT_WITHOUT_CUSTOM = ("""  You are now a seasoned solution professional in the field of the Enterprise information construction. 
 We need you to write the specific table of contents for Enterprise Information building solutions  with the background information.
 Backgrond information is"{demand}".""" + """
Please provide the specific table of contents for this document, strictly following the following requirements:
1. The output must be strictly in the specified language, {language}.
2. Answer strictly in the dictionary format like:
"""+COMMON_OUTPUT_FORMAT_EXAMPLE+
"""
3. The directory should be as specific and sufficient as possible, Each level of directory may contain multiple nested subdirectories.
4. Do not have extra spaces or line breaks.
5. Each directory title has practical significance.
6. leaf nodes only have 'title' key.
7.non-leaf nodes have the 'title' key and 'directory' key,and 'directory' key is an array contains the children. each element of the array is an object.
"""
)

## 建设方案目录生成，有自定义目录结构
CONSTRUCTION_DIRECTORY_PROMPT_WITH_CUSTOM = (
    """
    Please change the directory structure into the specific table of contents.The directory content provided for you is "{custom_directory}". Don't make assumptions, just turn the directory structure I provided you into the required data format, strictly following the following requirements:
    """+
    """
1. The output must be strictly in the specified language, {language}.
2. Output strictly in the required dictionary format like: """
+COMMON_OUTPUT_FORMAT_EXAMPLE+""".
3.Output the content strictly as the format provided for you,don't output other keys. 
4.You must consider the nested relationship of directory structures provided for you based on title number like '1', '1.1', '1.1.1', '2', '2.1'. And '1.1.1' and '2.1' are leaf nodes. Leaf nodes only have 'title' key and don't have 'directory' key.
5. Each level of directory may contain multiple nested subdirectories.
6. Do not have extra spaces or line breaks.
7.Fully understand the rules of the sample output directory format to ensure the right output format.
8. if the node key in the directory is 'directory',it must be an array.
9.Remembedr,Don't make any assumptions, just turn the directory content I provided you into the required data format.Even if I just provide you one title like '1 建设内容',just turn it into [{{"title":"1 建设内容"}}]


examples:
"""
+EXAMPLE_CASE
)


## 建设方案内容生成
CONSTRUCTION_CONTENT_PROMPT =(COMMON_CONSTRUCTION_PROMPT+"""
现在提供给你这个建设方案的总体目录和当前需要编写的小节题目，请综合考虑总体目录结构和小节标题以及项目背景，详细输出当前小节内容

方案内容的总体目录结构为:
{directory}
当前需要编写内容的小节标题为:
{current_section}

具体要求如下：
1.输出内容的语言必须用{language}。
2.输出内容大约{word_number}字左右。
3.输出内容不要分点描述，要整段整段输出。
4.输出内容要贴合当前小节标题所指内容。
5.输出内容不要有markdown语法结构，直接输出纯文本。
6.只输出正文内容，不要包含标题。
"""
)


class DocumentTypeList(Enum):
    """Indicates document type"""
    
    TECHNICAL="technical_documentation"
    CONSTRCTION="construction_plan"
    
REVIEW_DIRECTORY_DIRECTORY="""
请对以下json数据按照格式要求进行数据格式校验，如果数据内容不符合格式要求，需要你进行修复并输出正确的内容。如果数据内容符合格式要求，那么请将原始内容直接输出。数据内容："{directory}"。格式要求案例：'"""+COMMON_OUTPUT_FORMAT_EXAMPLE+"""'
具体要求如下：
1.直接输出json结果，不要输出其他内容
"""
