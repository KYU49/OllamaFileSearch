import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, pipeline
import numpy as np
from constants import EMBEDDING_MODEL, IS_QWEN

# # Requirements
# uv add flash-attn --no-build-isolation
# uv add protobuf
# uv add sentencepiece

tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(
    EMBEDDING_MODEL, 
    torch_dtype=torch.bfloat16, 
    device_map="auto", # 自動でGPUに割り当て
    trust_remote_code=True
).eval()

def vectorize(text):
	if IS_QWEN:
		# listで文書を受け取れるため、stringで受け取った場合は配列にする
		if isinstance(text, str):
			text = [text]
		# トークナイズ
		inputs = tokenizer(
			text,
			padding = True,
			truncationg = True,
			max_length = 32768,
			return_tensors="pt"
		)
		# GPUに移動
		inputs = {k: v.to(model.device) for k, v in inputs.items()}
		# 推論
		with torch.no_grad():
			outputs = model(**inputs)
		# 文書全体の意味を抽出するためにトークンごとのベクトルを平均化
		last_hidden_state = outputs.last_hidden_state
		attention_mask = inputs["attention_mask"]
		
		input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
		sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, 1)
		sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
		embeddings = sum_embeddings / sum_mask

		# L2 Normalization ---
		# 検索精度を保証するために必須。ベクトルの長さを1に揃える
		embeddings = F.normalize(embeddings, p=2, dim=1)
		
		return embeddings.cpu().numpy()

	else: 
		# BERTトークナイザーのロード
		tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, torch_dtype=torch.bfloat16)
		# BERTモデルのロード
		model = AutoModel.from_pretrained(EMBEDDING_MODEL, torch_dtype=torch.bfloat16)
		extractor = pipeline(task="feature-extraction", model=model, tokenizer = tokenizer)

		# BERTでベクトル化
		features = extractor(text)
		token_vectors = features[0]
		pooling_vector = np.mean(token_vectors, axis=0)
	
		return pooling_vector

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