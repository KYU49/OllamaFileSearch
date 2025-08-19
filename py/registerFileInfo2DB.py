from py.databaseFunction import db_cos_sim_search, db_insert_file_info
from getFileText import getFileText
from vectorize import vectorize

def detect(file = ""):
	# 内部テキストの変更がなければ、フラグなどのみ編集

	# ファイル内容をテキストとして取得
	text = getFileText(file)
	print(text)	#FIXME	
	# ファイル内容を登録するために、Vectorを取得
	#vector = vectorize(text)
	
	# ファイル内容の簡単な説明をLLMで作成

	# ファイルにscikit-Ollamaでラベル付け

	# 変更があったファイルについて、変更の種類によって場合分けし、変更をDBに反映するSQLを生成

	# SQLに反映

def main():
	detect("../.test/test.pdf")

if __name__ == "__main__":
	main()

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 