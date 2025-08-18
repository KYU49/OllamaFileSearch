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


# This code uses a model licensed under the MIT License, loaded directly from the Hugging Face Hub via the transformers library.
# The model itself is not stored or included in this repository.
#
# Please note that even though the model is not included here,
# usage is subject to the MIT License terms specified by the model author.
# Users must comply with the license conditions when using the model.
#
# For full license details, please refer to the model's page on the Hugging Face Hub.