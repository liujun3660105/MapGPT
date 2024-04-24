from enum import Enum
from langchain.text_splitter import RecursiveCharacterTextSplitter,SentenceTransformersTokenTextSplitter,SpacyTextSplitter,NLTKTextSplitter,TextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from Utils.device import get_device
from config.config import Config
CFG = Config()

separators=["\n", ".", "。", "!", "！", "?", "？", "；", ";", "……", "…"]

embeddings = HuggingFaceEmbeddings(
            model_name=CFG.EMBEDDING_PATH,
            model_kwargs={'device': get_device()},
            encode_kwargs={'normalize_embeddings': False})

class TextSplitter():
    @staticmethod
    def get_text_splitter(text_splitter_name: str,chunk_size = 50,chunk_overlap=5):
        if text_splitter_name == "recursive_char_text_splitter":
            return RecursiveCharacterTextSplitter(separators=separators,chunk_size=chunk_size,chunk_overlap=chunk_overlap,length_function=len)
        elif text_splitter_name == "nltk_text_splitter":
            return NLTKTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
        elif text_splitter_name == "spacy_text_splitter":
            return SpacyTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
        elif text_splitter_name == "semantic":
            return SemanticChunker(embeddings=embeddings)
        else:
            raise ValueError('Invalid split method')
        