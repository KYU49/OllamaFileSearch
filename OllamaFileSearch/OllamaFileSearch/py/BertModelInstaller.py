import os
import torch
from transformers import AutoTokenizer, AutoModel

def main():
	AutoTokenizer.from_pretrained(
		"sbintuitions/modernbert-ja-310m", 
		torch_dtype=torch.float16, 
		cache_dir=os.path.dirname(os.path.abspath(__file__)) + "/.cache"
	)
	AutoModel.from_pretrained(
		"sbintuitions/modernbert-ja-310m", 
		torch_dtype=torch.float16, 
		cache_dir=os.path.dirname(os.path.abspath(__file__)) + "/.cache"
	)
	
if __name__ == "__main__":
	main()