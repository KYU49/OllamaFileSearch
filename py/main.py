import sys
from databaseFunction import db_cos_sim_search, db_insert
from getFileText import getFileText
from appendMetadata import appendMetadata
from vectorize import vectorize
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

STORE_PATH = "./chroma.db"

def main():
	# 参考: note.com/jolly_azalea818/n/n763880f1668a
	if len(sys.argv) == 0:
		return 
	filePath = sys.argv[1]

	# ファイル内容からテキストを取得したdocument objectを取得
	doc = getFileText(filePath)

	# 内部テキストの変更がなければ、フラグなどのみ編集
	
	# メタデータを付与(LLMを使って、簡易説明と分類)
	appendMetadata(doc)

	# Moder BertのToken数が8192 (8192 * 0.96 = 7864.32文字)のため、分割する
	text_splitter = CharacterTextSplitter(
		separator="\n\n",
		chunk_size=3000,
		chunk_overlap=200
	)
	docs = text_splitter.split_documents(documents=[doc])

	# Databaseに反映
	embeddings = HuggingFaceEmbeddings(model_name="sbintuitions/modernbert-ja-310m")
	store = Chroma.from_documents(
		documents=docs,
		embedding=embeddings,
		persist_directory=STORE_PATH,
		collection_metadata={"hnsw:space": "cosine"}
	)

if __name__ == "__main__":
	main()

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 