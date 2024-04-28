from fastapi import File
from pydantic import BaseModel
from langchain.docstore.document import Document
from typing import List, Optional, Any

from langchain_community.document_loaders.pdf import UnstructuredPDFLoader, PyPDFLoader
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from controller.rag.loader.excel_loader import ExcelLoader
from langchain_community.document_loaders.powerpoint import UnstructuredPowerPointLoader
from Utils.const import get_root_path
from Utils.loader.my_recursive_url_loader import MyRecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter, SpacyTextSplitter, NLTKTextSplitter, TextSplitter, MarkdownTextSplitter
import urllib.request as request

import os
from enum import Enum
from datasource.vector_db.base import VectorDB


class FileFormat(Enum):
    PDF = "pdf"
    TXT = "txt"
    DOC = "docx"
    PPT = 'pptx'
    EXCEL = 'xlsx'
    IMAGE = 'jpg'
    MARKDOWN = 'md'


text_splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n", ".", "。", "!", "！", "?", "？", "；", ";", "……", "…", "、", "，", ",",
        " "
    ],
    chunk_size=50,
    chunk_overlap=5,
    length_function=len,
)
# text_splitter = SpacyTextSplitter(chunk_size=50,chunk_overlap=5)
# text_splitter = NLTKTextSplitter(chunk_size=50,chunk_overlap=5)


class LocalFile(BaseModel):
    file_id: str = ''
    file_name: str = ''
    # file_doc:Any = None
    file_format: str = FileFormat.PDF.value
    docs: Optional[List[Document]] = []
    file_path: str = ''
    text_splitter: Any = None
    local_file_path: str = ''

    # def __init__(self):
    #     ## 文件写入到后端data/upload文件夹下 TODO: 如果存到minIO中，则这里不需要存储
    #     self.save_file()

    def save_file(self):
        upload_path = os.path.join(get_root_path(), "data", "upload")
        file_dir = os.path.join(upload_path, self.file_id)
        os.makedirs(file_dir, exist_ok=True)
        self.local_file_path = os.path.join(file_dir, self.file_name)
        request.urlretrieve(self.file_path, self.local_file_path)
        # file_content = self.file_doc
        # with open(self.file_path, "wb+") as f:
        #     f.write(file_content)

    def split_file_to_document(self):
        if self.file_format == FileFormat.MARKDOWN.value:
            loader = UnstructuredMarkdownLoader(self.local_file_path)
            docs = loader.load()
            self.docs = self.text_splitter.split_documents(docs)
            # self.docs = MarkdownTextSplitter(chunk_size=20,chunk_overlap=5).split_documents(docs)

        # if self.file_name.lower().endswith(".docx"):
        elif self.file_format == FileFormat.DOC.value:
            loader = UnstructuredWordDocumentLoader(self.local_file_path)
            docs = loader.load()
            self.docs = self.text_splitter.split_documents(docs)
        # if self.file_name.lower().endswith(".pdf"):
        elif self.file_format == FileFormat.PDF.value:
            loader = PyPDFLoader(self.local_file_path)
            docs = loader.load()
            self.docs = self.text_splitter.split_documents(docs)
        elif self.file_format == FileFormat.TXT.value:
            loader = TextLoader(self.local_file_path)
            docs = loader.load()
            self.docs = self.text_splitter.split_documents(docs)
        elif self.file_format == FileFormat.EXCEL.value:
            loader = ExcelLoader(self.local_file_path, split_row_count=3)
            docs = loader.load()
            # self.docs = self.text_splitter.split_documents(docs)
            # excel是结构化数据，已经通过split_row_count分割成多个doc，直接存储在milvus中
            # TODO: 后续要对excle这种结构化存储和关系型数据库一起，直接通过sql语句进行查询，不通过矢量数据库
            self.docs = docs
        elif self.file_format == FileFormat.PPT.value:
            loader = UnstructuredPowerPointLoader(self.local_file_path)
            docs = loader.load()
            self.docs = self.text_splitter.split_documents(docs)
        else:
            raise TypeError(f"Got unknown file format {self.file_format}")
        for doc in self.docs:
            doc.metadata["file_id"] = self.file_id
            doc.metadata["file_name"] = self.file_name
            doc.metadata['page'] = doc.metadata.get('page', 1)

            # del doc.metadata['languages']

    # async def save_to_vectordb(self,vector_db:VectorDB):
    #     await vector_db.add_documents(self.docs)


class UrlFile(LocalFile):

    def split_file_to_document(self):
        loader = MyRecursiveUrlLoader(self.file_path)
        docs = loader.load()
        self.docs = self.text_splitter.split_documents(docs)
