import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel, pipeline
from langchain.embeddings.base import Embeddings
import sys

class ModernBERTEmbeddings(Embeddings):
    def __init__(self, model_name="sbintuitions/modernbert-ja-310m", batch_size=8, device=None):
        self.batch_size = batch_size

        # GPU自動判定
        self.device = device
        if self.device is None:
            if torch.cuda.is_available():
                self.device = 0  # GPU
            else:
                self.device = -1 # CPU

        # Flash Attention 2 利用可能か確認
        self.flash_attention = False
        try:
            import flash_attn
            self.flash_attention = True
        except ImportError:
            pass

        if self.flash_attention and self.device >= 0:
            print("Flash Attention 2 detected: 高速化を有効化")
        else:
            if self.device >= 0:
                print("GPUのみ利用、Flash Attention 2なし")
            else:
                print("CPUモードで実行")

        # トークナイザーとモデルロード
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        if self.device >= 0:
            self.model.to(torch.device("cuda"))
        self.model.eval()

        # pipeline 用意
        self.extractor = pipeline(
            task="feature-extraction",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
            batch_size=self.batch_size
        )

    def _vectorize_text(self, text):
        features = self.extractor(text)
        token_vectors = features[0]
        pooling_vector = np.mean(token_vectors, axis=0)
        return pooling_vector.tolist()

    def embed_documents(self, texts):
        vectors = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i+self.batch_size]
            batch_vectors = self.extractor(batch_texts)
            for features in batch_vectors:
                token_vectors = features
                pooling_vector = np.mean(token_vectors, axis=0)
                vectors.append(pooling_vector.tolist())
        return vectors

    def embed_query(self, text):
        return self._vectorize_text(text)