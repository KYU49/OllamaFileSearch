import sys
import os
from getFileText import getFileText
from appendMetadata import appendMetadata
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings

STORE_PATH = os.getcwd() + "/chromadb"
COLLECTION_NAME = "ollama_file_collection"

def getFilePath():
	# 参考: note.com/jolly_azalea818/n/n763880f1668a
	if len(sys.argv) == 0:
		return None
	return sys.argv[1]

def main():
	filePath = getFilePath()
	if (not filePath) or (not os.path.isfile(filePath)):
		return

	# ファイル内容からテキストを取得したdocument objectを取得
	doc = getFileText(filePath)

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
	embeddings = ModernBERTEmbeddings()
	db = Chroma(
		persist_directory=STORE_PATH,
		embedding_function=embeddings,
		collection_name=COLLECTION_NAME,
		collection_metadata={"hnsw:space": "cosine"},
		
	)
	# 既にあったら削除しておく
	for d in docs:
		source = d.metadata.get("source")
		if source:
			id2delete = db.get(where={"source": source})
			if len(id2delete.get("ids")) > 0:
				db.delete(ids = id2delete.get("ids"))
	# 実際のinsert
	db.add_documents(docs)

if __name__ == "__main__":
	main()

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 