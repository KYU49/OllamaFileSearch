import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import numpy as np

# # Requirements
# uv add flash-attn --no-build-isolation
# uv add protobuf
# uv add sentencepiece

def vectorize(text):
	# BERTトークナイザーのロード
	tokenizer = AutoTokenizer.from_pretrained("sbintuitions/modernbert-ja-310m", torch_dtype=torch.bfloat16)
	# BERTモデルのロード
	model = AutoModel.from_pretrained("sbintuitions/modernbert-ja-310m", torch_dtype=torch.bfloat16)
	extractor = pipeline(model=model, task = "feature-extraction", tokenizer = tokenizer)

	# BERTでベクトル化
	features = extractor(text)
	token_vectors = features[0]
	cls_vector = np.mean(token_vectors, axis=0)
	
	return cls_vector

def cos_sim(v1, v2):
	return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


