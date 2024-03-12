#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
@Time    : 2023/9/4 15:40:40
@Author  : Stitch-z
@File    : tutorial_assistant.py
"""

from datetime import datetime
from typing import Dict

# from metagpt.actions.write_tutorial import WriteContent, WriteDirectory
from .action import WriteContent, WriteDirectory,RviewDirectory
from .prompt import DocumentTypeList
# from metagpt.const import TUTORIAL_PATH
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message
from metagpt.utils.file import File
from Utils.const import TUTORIAL_PATH
from Utils.data_handle import json_to_markdown,find_leaf_nodes
# from Utils import const






class TutorialAssistant(Role):
    """Tutorial assistant, input one sentence to generate a tutorial document in markup format.

    Args:
        name: The name of the role.
        profile: The role profile description.
        goal: The goal of the role.
        constraints: Constraints or requirements for the role.
        language: The language in which the tutorial documents will be generated.
    """

    name: str = "Stitch"
    profile: str = "Tutorial Assistant"
    goal: str = "Generate tutorial documents"
    constraints: str = "Strictly follow Markdown's syntax, with neat and standardized layout"
    language: str = "Chinese"

    # demand: str = ""
    main_title: str = ""
    total_content: str = ""
    demand:str = ""
    document_type:DocumentTypeList
    directory:str=""
    word_number:int = 200
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([WriteDirectory(language=self.language,document_type=self.document_type,directory=self.directory),RviewDirectory()])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)
    async def _handle_directory(self, titles: list) -> Message:
        """Handle the directories for the tutorial document.

        Args:
            titles: A dictionary containing the titles and directory structure,
                    such as {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}

        Returns:
            A message containing information about the directory.
        """
        # self.main_title = titles.get("title") #文章标题
        # directory = titles.get("directory")#文章内容
        directory = titles
        markdown_directory = json_to_markdown(directory)
        # directory = f"{self.main_title}\n"
        # self.total_content += f"# {self.main_title}"
        self.total_content = markdown_directory # 目录结构变成markdown形式，作为内容编写action的初始内容，后面action编写的内容要插入到对应的位置，输出给前端
        actions = list()
        content_node_list = find_leaf_nodes(directory)## 获取所有叶子节点,叶子节点需要添加内容
        for leaf_node in content_node_list:
            actions.append(WriteContent(language=self.language,current_section=leaf_node, directory=directory,document_type=self.document_type,word_number = self.word_number))
        # for first_dir in titles.get("directory"):
        #     actions.append(WriteContent(language=self.language, directory=first_dir))
        #     key = list(first_dir.keys())[0]
        #     directory += f"- {key}\n"
        #     for second_dir in first_dir[key]:
        #         directory += f"  - {second_dir}\n"
                
        self.set_actions(actions)

    async def _act(self) -> Message:
        """Perform an action as determined by the role.

        Returns:
            A message containing the result of the action.
        """
        todo = self.rc.todo
        if type(todo) is WriteContent:
            resp = await todo.run(demand=self.demand)
            logger.info(resp)
            if self.total_content != "":
                self.total_content += "\n\n\n"
            self.total_content += resp
            # yield self.total_content
            return Message(content=resp, role=self.profile)
        else:
            msg = self.get_memories(k=1)[0]
            resp = await todo.run(msg.content)
            if type(todo) is RviewDirectory:
                return resp
            msg = Message(content=resp, role=self.profile,
                      cause_by=type(todo)) # 这里第二次执行的是
        self.rc.memory.add(msg)
        return msg
    # async def _act(self) -> Message:
    #     """Perform an action as determined by the role.

    #     Returns:
    #         A message containing the result of the action.
    #     """
    #     todo = self.rc.todo
    #     if type(todo) is WriteDirectory:
    #         msg = self.rc.memory.get(k=1)[0]
    #         self.demand = msg.content
    #         resp = await todo.run(demand=self.demand)
    #         logger.info(resp)
    #         await self._handle_directory(resp)
    #         # return Message(content=resp, role=self.profile)
    #         return await super().react()
    #     resp = await todo.run(demand=self.demand)
    #     logger.info(resp)
    #     if self.total_content != "":
    #         self.total_content += "\n\n\n"
    #     self.total_content += resp
    #     # yield self.total_content
    #     return Message(content=resp, role=self.profile)



    # async def react(self) -> Message:
    #     msg = await super().react()
    #     root_path = TUTORIAL_PATH / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #     await File.write(root_path, f"{self.main_title}.md", self.total_content.encode("utf-8"))
    #     msg.content = str(root_path / f"{self.main_title}.md")
    #     return msg

