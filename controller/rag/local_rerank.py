import time
from transformers import AutoTokenizer
from copy import deepcopy
from typing import List
from tritonclient import grpc as grpcclient
from config.config import Config
import numpy as np
from BCEmbedding import RerankerModel 

config = Config()


class LocalRerankBackend:
    def __init__(self):
        self.model = RerankerModel(model_name_or_path=config.LOCAL_RERANK_MODEL_PATH)
    def predict(self,
                query: str,
                passages: List[str],):
        sentence_pairs = [[query, passage] for passage in passages]
        scores = self.model.compute_score(sentence_pairs)
        return scores
        # rerank_results = self.model.rerank(query, passages)