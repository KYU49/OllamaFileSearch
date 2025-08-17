from vectorize import vectorize

def main(prompt = ""):
	# 変更があったファイルについて、変更の種類によって場合分けし、変更をDBに反映するSQLを生成
	sqlQuery = ""
	
	# 内部テキストの変更がなければ、フラグなどのみ編集

	# ファイル内容をテキストとして取得
	
	# ファイル内容を登録するために、Vectorを取得
	vector = vectorize(prompt)

	# SQLに反映



if __name__ == "__main__":
	main()
