import sys
import json
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from constants import DB_PATH, BERT_MODEL

prompt = sys.argv[1]

# Chroma DB準備
persist_directory = DB_PATH
embedding_model = HuggingFaceEmbeddings(
	model_name=BERT_MODEL
)
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)
retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 20})

# 検索
docs = retriever.get_relevant_documents(prompt)
# JSON化してPHPに返す
results = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
print(json.dumps(results, ensure_ascii=False))