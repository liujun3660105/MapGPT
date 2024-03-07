COMMON_PROMPT = """
You are now a seasoned technical professional in the field of the internet. 
We need you to write a technical tutorial with the topic "{topic}".
"""

# DIRECTORY_PROMPT = (
#     COMMON_PROMPT
#     + """
# Please provide the specific table of contents for this tutorial, strictly following the following requirements:
# 1. The output must be strictly in the specified language, {language}.
# 2. Answer strictly in the dictionary format like {{"title": "xxx", "directory": [{{"dir 1": ["sub dir 1", "sub dir 2"]}}, {{"dir 2": ["sub dir 3", "sub dir 4"]}}]}}.
# 3. The directory should be as specific and sufficient as possible, with a primary and secondary directory.The secondary directory is in the array.
# 4. Do not have extra spaces or line breaks.
# 5. Each directory title has practical significance.
# """
# )

DIRECTORY_PROMPT = (
    COMMON_PROMPT
    + """
Please provide the specific table of contents for this tutorial, strictly following the following requirements:
1. The output must be strictly in the specified language, {language}.
2. Answer strictly in the dictionary format like 
[
    {{
        "title":"1xxx",
        "directory":[
            {{
                "title":"1.1xxx",
                "directory":["1.1.1xxx","1.1.2xxx"]
            }},
            {{
                "directory":["1.2xxx","1.3xxxx"]
            }}
        ]
    }},
    {{
        "title":"2xxx",
        "directory":[
            {{
                "title":"2.1xxx",
                "directory":["2.1.1xxx","2.1.2xxx"]
            }},
            {{
                "title":"2.2:xxx",
                "directory":["2.2.1xxx","2.2.2xxx"]
            }},
            {{
                "title":"2.3:xxx",
                "directory":[
                    {{
                        "title":"2.3.1xxx",
                        "directory":["2.3.1.1xxx","2.3.1.2xxx"]
                    }},
                    {{
                        "title":"2.3.2xxx",
                         "directory":["2.3.2.1xxx","2.3.2.2xxx"]
                    }}
                ]
            }}
        ]
    }}
].
3. The directory should be as specific and sufficient as possible, Each level of directory may contain multiple nested subdirectories. When the content of the directory is an array, it includes the directories of the entire article's leaf nodes.
4. Do not have extra spaces or line breaks.
5.Fully understand the rules of the sample directory numbering to ensure the correctness of the directory numbers you output.
6. Each directory title has practical significance.
"""
)



# CONTENT_PROMPT = (
#     COMMON_PROMPT
#     + """
# Now I will give you the module directory titles for the topic. 
# Please output the detailed principle content of this title in detail. 
# If there are code examples, please provide them according to standard code specifications. 
# Without a code example, it is not necessary.

# The module directory titles for the topic is as follows:
# {directory}

# Strictly limit output according to the following requirements:
# 1. Follow the Markdown syntax format for layout.
# 2. If there are code examples, they must follow standard syntax specifications, have document annotations, and be displayed in code blocks.
# 3. The output must be strictly in the specified language, {language}.
# 4. Do not have redundant output, including concluding remarks.
# 5. Strict requirement not to output the topic "{topic}".
# """
# )

CONTENT_PROMPT = (
    COMMON_PROMPT
    + """
Now I will give you the overall directory titles for the topic and the current section title. Please combine the overall directory structure to output the content of the current section.
Please output the detailed principle content of current section in detail. 
If there are code examples, please provide them according to standard code specifications. 

Without a code example, it is not necessary.

The module directory titles for the topic is as follows:
{directory}
The current section to be written as fowllow:
{current_section}

Strictly limit output according to the following requirements:
1. Follow the Markdown syntax format for layout.
2. If there are code examples, they must follow standard syntax specifications, have document annotations, and be displayed in code blocks.
3. The output must be strictly in the specified language, {language}.
4. Do not have redundant output, including concluding remarks.
5. Strict requirement not to output the topic "{topic}".
6. Only output the content of the current section, without including any other titles.
"""
)