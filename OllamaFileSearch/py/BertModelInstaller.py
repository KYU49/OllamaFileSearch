import os
from transformers import AutoTokenizer

def main():
	self.tokenizer = AutoTokenizer.from_pretrained(
		"sbintuitions/modernbert-ja-310m", 
		torch_dtype=torch.float16, 
		cache_dir=CACHE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/.cache"
	)
	
if __name__ == "__main__":
	main()