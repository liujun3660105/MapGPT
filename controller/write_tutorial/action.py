from typing import Dict
from metagpt.actions import Action
from metagpt.schema import Message
# from metagpt.prompts.tutorial_assistant import CONTENT_PROMPT, DIRECTORY_PROMPT
from metagpt.utils.common import OutputParser
from .prompt import get_content_prompt,get_directory_prompt,DocumentTypeList,TECHNICAL_DIRECTORY_PROMPT_WITH_CUSTOM,TECHNICAL_DIRECTORY_PROMPT_WITHOUT_CUSTOM,CONSTRUCTION_DIRECTORY_PROMPT_WITH_CUSTOM,CONSTRUCTION_DIRECTORY_PROMPT_WITHOUT_CUSTOM,CONSTRUCTION_CONTENT_PROMPT,TECHNICAL_CONTENT_PROMPT,REVIEW_DIRECTORY_DIRECTORY


    

class WriteDirectory(Action):
    """Action class for writing tutorial directories.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    name: str = "WriteDirectory"
    language: str = "Chinese"
    document_type:DocumentTypeList=DocumentTypeList.TECHNICAL
    directory:str=""

    async def run(self, demand: str, *args, **kwargs) -> Dict:
        """Execute the action to generate a tutorial directory according to the demand.

        Args:
            demand: The tutorial demand.

        Returns:
            the tutorial directory information, including {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}.
        """
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory).format(demand=demand, language=self.language,direcotry = self.directory)
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory)
        # prompt = prompt.format(demand=demand, language=self.language, aa = self.directory)
        prompt = ''
        if self.document_type is DocumentTypeList.TECHNICAL and self.directory:
            prompt = TECHNICAL_DIRECTORY_PROMPT_WITH_CUSTOM.format(demand=demand, language=self.language, custom_directory = self.directory)
        if self.document_type is DocumentTypeList.TECHNICAL and not self.directory:
            prompt = TECHNICAL_DIRECTORY_PROMPT_WITHOUT_CUSTOM.format(demand=demand, language=self.language)
        if self.document_type is DocumentTypeList.CONSTRCTION and self.directory:
            prompt = CONSTRUCTION_DIRECTORY_PROMPT_WITH_CUSTOM.format(demand=demand, language=self.language, custom_directory = self.directory)
        if self.document_type is DocumentTypeList.CONSTRCTION and not self.directory:
            prompt = CONSTRUCTION_DIRECTORY_PROMPT_WITHOUT_CUSTOM.format(demand=demand, language=self.language)
        return await self._aask(prompt=prompt)
  


class RviewDirectory(Action):
    """Review the write-directory output as required format.

    Args:
        directory: The output of the write-directory action.
        language: The language to output, default is "Chinese".
    """

    name: str = "ReviewDirectory"
    language: str = "Chinese"
    directory:str=""

    async def run(self, directory: str, *args, **kwargs) -> Dict:
        """Execute the action to review the directory according to the demand and output the standard content

        Args:
            directory: The write-directory content.

        Returns:
            the tutorial directory information, including {"title": "xxx", "directory": [{"title": "xxx","directory":[{"title":"xxx"},{"title":"xxx"}]}]}.
        """
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory).format(demand=demand, language=self.language,direcotry = self.directory)
        # prompt = get_directory_prompt(value = self.document_type,directory=self.directory)
        # prompt = prompt.format(demand=demand, language=self.language, aa = self.directory)
        prompt = REVIEW_DIRECTORY_DIRECTORY.format(directory=directory)
        resp = await self._aask(prompt=prompt)
        resp = resp.replace('\n','')
        return OutputParser.extract_struct(resp, list)




class WriteContent(Action):
    """Action class for writing tutorial content.

    Args:
        name: The name of the action.
        directory: The content to write.
        language: The language to output, default is "Chinese".
    """

    name: str = "WriteContent"
    directory: list = []
    document_type:DocumentTypeList
    current_section:str
    language: str = "Chinese"
    word_number:int = 200

    async def run(self, demand: str, *args, **kwargs) -> str:
        """Execute the action to write document content according to the directory and demand.

        Args:
            demand: The tutorial demand.

        Returns:
            The written tutorial content.
        """
        prompt = ''
        if self.document_type is DocumentTypeList.TECHNICAL:
            prompt = TECHNICAL_CONTENT_PROMPT.format(demand=demand, language=self.language,current_section = self.current_section,directory=self.directory,word_number = self.word_number)
        else:
            prompt = CONSTRUCTION_CONTENT_PROMPT.format(demand=demand, language=self.language,current_section = self.current_section,directory=self.directory,word_number = self.word_number)
        # if self.document_type is DocumentTypeList.TECHNICAL and not self.directory:
        #     prompt = TECHNICAL_DIRECTORY_PROMPT_WITHOUT_CUSTOM.format(demand=demand, language=self.language)
        # if self.document_type is DocumentTypeList.CONSTRCTION and self.directory:
        #     prompt = CONSTRUCTION_DIRECTORY_PROMPT_WITH_CUSTOM.format(demand=demand, language=self.language, custom_directory = self.directory)
        # if self.document_type is DocumentTypeList.CONSTRCTION and not self.directory:
        #     prompt = CONSTRUCTION_DIRECTORY_PROMPT_WITHOUT_CUSTOM.format(demand=demand, language=self.language)
        # prompt = get_content_prompt(self.document_type).format(demand=demand,current_section = self.current_section, language=self.language, directory=self.directory)
        return await self._aask(prompt=prompt)
