
#1.根据文档进行普通的问答
#2.招标文件和投标文件的智慧问答
#3.根据问题自动筛选出不符合条件的部分


# from metagpt.actions.write_tutorial import WriteContent, WriteDirectory
from .action import Retriever
# from metagpt.const import TUTORIAL_PATH
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode
from metagpt.schema import Message
from metagpt.utils.repair_llm_raw_output import extract_state_value_from_output
from metagpt.provider import HumanProvider
from metagpt.actions import Action,ActionOutput
from metagpt.actions.action_node import ActionNode
from typing import TYPE_CHECKING, Iterable, Optional, Set, Type, Union
from metagpt.actions.add_requirement import UserRequirement
from langchain_community.vectorstores.chroma import Chroma

from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
# from Utils import const

class BidingAssistant(Role):
    """geoAnalysis assistant, follow user's requirements and get the right result.

    Args:
        name: The name of the role.
        profile: The role profile description.
        goal: The goal of the role.
        constraints: Constraints or requirements for the role.
        language: The language in which the tutorial documents will be generated.
    """

    name: str = "Stitch"
    profile: str = "GeoAnalysis Assistant based on pg spatial database"
    goal: str = "based on user requirements,analysis the data from pg spatial database and generate the sql statements"
    constraints: str = ""
    language: str = "Chinese"
    user_requirement:str = ""
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([Retriever(language=self.language)])
        self._set_react_mode(react_mode=RoleReactMode.BY_ORDER.value)
    
    
    async def run(self, with_message=None) -> Message | None:
        """Observe, and think and act based on the results of the observation"""
        if with_message:
            msg = None
            if isinstance(with_message, str):
                msg = Message(content=with_message)
            elif isinstance(with_message, Message):
                msg = with_message
            elif isinstance(with_message, list):
                msg = Message(content="\n".join(with_message))
            if not msg.cause_by:
                msg.cause_by = UserRequirement
            self.put_message(msg)
        if not await self._observe():
            # If there is no new information, suspend and wait
            logger.debug(f"{self._setting}: no news. waiting.")
            return

        rsp = await self.react()

        # Reset the next action to be taken.
        self.set_todo(None)
        # Send the response message to the Environment object to have it relay the message to the subscribers.
        self.publish_message(rsp)
        return rsp
        
    async def run(self, with_message=None) -> Message | None:
        """Observe, and think and act based on the results of the observation"""
        self.user_requirement = with_message
        if with_message:
            msg = None
            if isinstance(with_message, str):
                msg = Message(content=with_message)
            elif isinstance(with_message, Message):
                msg = with_message
            elif isinstance(with_message, list):
                msg = Message(content="\n".join(with_message))
            if not msg.cause_by:
                msg.cause_by = UserRequirement
            self.put_message(msg)
        if not await self._observe():
            # If there is no new information, suspend and wait
            logger.debug(f"{self._setting}: no news. waiting.")
            return

        rsp = await self.react()

        # Reset the next action to be taken.
        self.set_todo(None)
        # Send the response message to the Environment object to have it relay the message to the subscribers.
        self.publish_message(rsp)
        return rsp
        
    async def _think(self) -> bool:
        """Consider what to do and decide on the next course of action. Return false if nothing can be done."""
        if len(self.actions) == 1:
            # If there is only one action, then only this one can be performed
            self._set_state(0)

            return True

        if self.recovered and self.rc.state >= 0:
            self._set_state(self.rc.state)  # action to run from recovered state
            self.recovered = False  # avoid max_react_loop out of work
            return True

        # prompt = self._get_prefix()
        prompt = PREFIX_TEMPLATE.format(profile = self.profile,name=self.name,goal=self.goal,user_requirement=self.user_requirement)
        history_message ="\n".join([f"{message.cause_by}:{message.content}" for message in self.rc.memory.get()])
        prompt += STATE_TEMPLATE.format(
            history=history_message,
            states="\n".join(self.states),
            n_states=len(self.states) - 1,
            previous_state=self.rc.state,
        )

        next_state = await self.llm.aask(prompt)
        next_state = extract_state_value_from_output(next_state)
        logger.debug(f"{prompt=}")

        if (not next_state.isdigit() and next_state != "-1") or int(next_state) not in range(-1, len(self.states)):
            logger.warning(f"Invalid answer of state, {next_state=}, will be set to -1")
            next_state = -1
        else:
            next_state = int(next_state)
            if next_state == -1:
                logger.info(f"End actions with {next_state=}")
        self._set_state(next_state)
        return True
    
    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        msg = self.get_memories(k=1)[0]  # find the most recent
        response = await self.rc.todo.run(self.user_requirement,msg.content)
        if isinstance(response, (ActionOutput, ActionNode)):
            msg = Message(
                content=response.content,
                instruct_content=response.instruct_content,
                role=self._setting,
                cause_by=self.rc.todo,
                sent_from=self,
            )
        elif isinstance(response, Message):
            msg = response
        else:
            msg = Message(content=response, role=self.profile, cause_by=self.rc.todo, sent_from=self)
        self.rc.memory.add(msg)

        return msg
    
    def set_actions(self, actions: list[Union[Action, Type[Action]]]):
        """Add actions to the role.

        Args:
            actions: list of Action classes or instances
        """
        self._reset()
        for action in actions:
            if not isinstance(action, Action):
                i = action(context=self.context)
            else:
                if self.is_human and not isinstance(action.llm, HumanProvider):
                    logger.warning(
                        f"is_human attribute does not take effect, "
                        f"as Role's {str(action)} was initialized using LLM, "
                        f"try passing in Action classes instead of initialized instances"
                    )
                i = action
            self._init_action(i)
            self.actions.append(i)
            self.states.append(f"{len(self.actions) - 1}. {action.name}:{action.desc}")

