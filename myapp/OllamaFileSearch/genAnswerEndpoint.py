import sys
import json
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings
from constants import DB_PATH, COLLECTION_NAME
from PageContentRetrieverWrapper import PageContentRetrieverWrapper


SYSTEM_PROMPT = """
First, assess whether the user's question is addressed or partially addressed by the search results.

If the search results contain information that is likely to help answer or clarify the question, even partially, treat it as relevant. 
Do not require an exact match of wording—conceptual relevance is sufficient.

Only if there is truly no meaningful or related information at all, respond:
"No relevant files were found." (translated into the same language with user's question).

If the information is relevant, generate a clear and concise answer in HTML format (not Markdown), using only the search results as your source. 
You may summarize, reorganize, or restate the relevant points to directly 

# User's Question
{question}

# Search Results
{context}
"""


# --- 引数取得 ---
userPrompt = sys.argv[1]

embeddings = ModernBERTEmbeddings()
db = Chroma(
	persist_directory=DB_PATH,
	embedding_function=embeddings,
	collection_name=COLLECTION_NAME,
	collection_metadata={"hnsw:space": "cosine"},
)

retriever = PageContentRetrieverWrapper(retriever=db.as_retriever(search_type="similarity", search_kwargs={"k": 3}))

llm = OllamaLLM(
	model="gpt-oss:20b", 
	base_url="http://localhost:11434", 
	streaming=True, 
	temperature=0,
	num_ctx=8192	# 8192で14GBくらいになる
)

# --- SSE用コールバック ---
class SSECallbackHandler(BaseCallbackHandler):
	def on_llm_new_token(self, token: str, **kwargs):
		# SSE形式で送信
		print(json.dumps({"token": token}), flush=True)

	def on_llm_end(self, response, **kwargs):
		# 終了を通知
		print("[DONE]", flush=True)

promptTemplate =PromptTemplate(
	template=SYSTEM_PROMPT,
	input_variables=["context", "question"]
)

# --- RAG用Chain構築 ---
chainWithRag = RetrievalQA.from_chain_type(
	llm=llm,
	retriever=retriever,
	chain_type="stuff",		# "stuff" (そのまま渡す), "map_reduce" (文書ごとに部分的な回答を生成してまとめる), "refine" (ざっくりした回答を作った後、文書を順番に見て洗練する) など用途に応じて選択。
	return_source_documents=False,
	chain_type_kwargs={"prompt": promptTemplate},
)

for chunk in chainWithRag.stream(userPrompt, config={"callbacks": [SSECallbackHandler()]}):
	pass	# SSEは逐次コールバックで送信されるのでここでは何もしない

