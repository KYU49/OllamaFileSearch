import sys
import io
import json
from ModernBertEmbeddings import ModernBERTEmbeddings
from constants import DB_PATH, COLLECTION_NAME
from langchain_chroma.vectorstores import Chroma

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

# 検索
docsAndScores = db.similarity_search_with_score(prompt, k=20)
results = [{"documents": getattr(doc, "page_content", getattr(doc, "documents", "")), "metadata": {**doc.metadata, "similality": 1 - similality}} for doc, similality in docsAndScores]

print(json.dumps(results, ensure_ascii=False))