from typing import Any, Type
from metagpt.actions.action_node import ActionNode
from metagpt.actions.action import Action
from metagpt.roles.role import Role
import re
from metagpt.schema import Message
from metagpt.logs import logger
import asyncio



SIMPLE_THINK_NODE = ActionNode(
    key='simple think node',
    expected_type=str,
    instruction="""
        Think about what list of numbers you need to generate
    """,
    example=''
)


SIMPLE_CHECK_NODE = ActionNode(
    key="Simple CHECK Node",
    expected_type=str,
    instruction="""
            Please provide the number list for me, strictly following the following requirements:
            1. Answer strictly in the list format like [1,2,3,4]
            2. Do not have extra spaces or line breaks.
            Return the list here:
            请严格按照以下要求为我提供号码清单：
            1. 严格按照 [1,2,3,4] 这样的列表格式作答
            2. 不要有额外的空格或换行。
            在此返回列表：
            """,
    example="[1,2,3,4]"
            "[4,5,6]",
 )


class THINK_NODES(ActionNode):
    def __init__(self, name: str = 'Think Nodes', expected_type= str, instruction='', example=''):
        super().__init__(key=name, expected_type=str, instruction=instruction, example=example)
        self.add_children([SIMPLE_THINK_NODE,SIMPLE_CHECK_NODE])
        
    async def fill(self,context, llm, schema="raw", mode="auto", strgy="complex"):
        self.set_llm(llm)
        self.set_context(context)
        if self.schema:
            schema = self.schema

        if strgy == "simple":
            return await self.simple_fill(schema=schema, mode=mode)
        elif strgy == "complex":
            # 这里隐式假设了拥有children
            child_context = context    # 输入context作为第一个子节点的context
            for _, i in self.children.items():
                i.set_context(child_context)    # 为子节点设置context
                child = await i.simple_fill(schema=schema, mode=mode)
                child_context = child.content    # 将返回内容（child.content）作为下一个子节点的context

            self.content = child_context    # 最后一个子节点返回的内容设置为父节点返回内容（self.content）
            return self
        
        
class ThinkAction(Action):
    """
    Action that think
    """

    def __init__(self, name="ThinkAction", context=None, llm=None):
        super().__init__()
        self.node = THINK_NODES()    # 初始化Action时，初始化一个THINK_NODE实例并赋值给self.node

    async def run(self, instruction) -> list:
        PROMPT = """
            You are now a number list generator, follow the instruction {instruction} and 
            generate a number list to be printed please.
            您现在是数字列表生成器，请按照指令 {instruction} 生成数字列表并打印出来。
            生成一个数字列表并打印出来。
            """

        prompt = PROMPT.format(instruction=instruction)
        rsp_node = await self.node.fill(context=prompt, llm=self.llm, schema="raw", strgy="complex")    # 运行子节点，获取返回（返回格式为ActionNode）（注意设置 schema="raw" ）
        rsp = rsp_node.content    # 获取返回的文本内容

        rsp_match = self.find_in_brackets(rsp)    # 按列表格式解析返回的文本内容，定位“[”与“]”之间的内容

        try:
            rsp_list = list(map(int, rsp_match[0].split(',')))    # 按列表格式解析返回的文本内容，按“,”对内容进行分割，并形成一个python语法中的列表

            return rsp_list
        except:
            return []
            
    @staticmethod
    def find_in_brackets(s):
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, s)
        return match
    
    
    
class SimplePrint(Action):
    """
    Action that print the num inputted
    """
    input_num:int = 0

    def __init__(self, name="SimplePrint", input_num:int=0):
        super().__init__()

        self.input_num = input_num

    async def run(self, **kwargs):
        print(str(self.input_num) + "\n")    # 打印输入数字
        return 0
    
    
class Printer(Role):
    def __init__(self, name="Jerry", profile="Printer", goal="Print the number", constraints=""):
        super().__init__()
        self.set_actions([ThinkAction])
        
        
    async def _think(self) -> None:
        if self.rc.todo is None:
            self._set_state(0)
            return
        if self.rc.state + 1 < len(self.states):
            self._set_state(self.rc.state + 1)
        else:
            self.rc.todo = None
            
    async def _react(self)->Message:
        """"""
        while True:
            await self._think()
            if self.rc.todo is None:
                break
            msg = await self._act()
        return msg
    
    
    async def _prepare_print(self, num_list:list) -> Message:
        """Add actions"""
        actions = list()
        for num in num_list:
            actions.append(SimplePrint(input_num=num))    # 根据返回的列表，设置一系列的SimplePrint

        self.set_actions(actions)    # 初始化动作
        self.rc.todo = None
        return Message(content=str(num_list))
    
    
    async def _act(self) -> Message:
        """Action"""
        todo = self.rc.todo

        if type(todo) is ThinkAction :
            msg = self.rc.memory.get(k=1)[0]
            self.goal = msg.content
            resp = await todo.run(instruction=self.goal)
            return await self._prepare_print(resp)    # 执行完ThinkAction后，根据返回的列表，设置SimplePrint
        
        resp = await todo.run()
        resp = str(resp)
        return Message(content=resp, role=self.profile)
    
    
async def main():
    msg = "Provide the first 10 numbers of the Fibonacci series"
    role = Printer()
    logger.info(msg)
    result = await role.run(msg)
    logger.info(result)


if __name__ == '__main__':
    asyncio.run(main())