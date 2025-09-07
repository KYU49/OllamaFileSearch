import torch
from transformers import AutoTokenizer, AutoModel
from constants import EMBEDDING_MODEL, CACHE_PATH

def main():
	# Embedding用のモデルを先にダウンロードしておく。
	AutoTokenizer.from_pretrained(
		EMBEDDING_MODEL, 
		torch_dtype=torch.float16, 
		cache_dir=CACHE_PATH
	)
	AutoModel.from_pretrained(
		EMBEDDING_MODEL, 
		torch_dtype=torch.float16, 
		cache_dir=CACHE_PATH
	)
	
	
if __name__ == "__main__":
	main()