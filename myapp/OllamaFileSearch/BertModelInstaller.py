import torch
from transformers import AutoTokenizer, AutoModel
from constants import BERT_MODEL, CACHE_PATH

def main():
	AutoTokenizer.from_pretrained(
		BERT_MODEL, 
		torch_dtype=torch.float16, 
		cache_dir=CACHE_PATH
	)
	AutoModel.from_pretrained(
		BERT_MODEL, 
		torch_dtype=torch.float16, 
		cache_dir=CACHE_PATH
	)
	
if __name__ == "__main__":
	main()