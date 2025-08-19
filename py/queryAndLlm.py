from vectorize import vectorize, cos_sim

def main(prompt = ""):
	# ユーザーの入力内容をvector化
	vector = vectorize(prompt)

	# DBで検索して、該当ファイルのテキストを取得
	fileText = queryVector(vector)

	# テキスト内容を入れて、LLMを叩く
	genOutput(prompt, fileText)

def queryVector(vector):
	pass

def genOutput(prompt, content):
	pass

if __name__ == "__main__":
	main()
