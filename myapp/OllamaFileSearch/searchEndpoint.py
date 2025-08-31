import os
import sys
import io
import json
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings
from constants import DB_PATH, COLLECTION_NAME

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

prompt = sys.argv[1]

# Chroma DB準備
embeddings = ModernBERTEmbeddings()
db = Chroma(
	persist_directory=DB_PATH,
	embedding_function=embeddings,
	collection_name=COLLECTION_NAME,
	collection_metadata={"hnsw:space": "cosine"}
)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 20})

# 検索
docs = retriever.invoke(prompt)
# JSON化してPHPに返す
results = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs]
print(json.dumps(results, ensure_ascii=False))