from transformers import BertTokenizer, BertModel
import torch

def vecterize(text):
	# BERTトークナイザーのロード
	tokenizer = BertTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")

	# BERTモデルのロード
	model = BertModel.from_pretrained("cl-tohoku/bert-base-japanese")

	# 文節ごとに区切る処理（MeCabを使っても良いが、BERTのトークナイザーでそのまま処理可能）
	inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

	# BERTでベクトル化
	with torch.no_grad():
		outputs = model(**inputs)

	# BERTの出力（[CLS]トークンのベクトル）
	last_hidden_states = outputs.last_hidden_state

	# 最後の隠れ層の状態を取り出す (shape: (batch_size, sequence_length, hidden_size))
	sentence_embedding = last_hidden_states.mean(dim=1)  # 平均を取ることで文全体の埋め込みベクトル

	# 768次元ベクトル（文全体の埋め込み）
	sentence_embedding = sentence_embedding.squeeze().numpy()
	
	return sentence_embedding