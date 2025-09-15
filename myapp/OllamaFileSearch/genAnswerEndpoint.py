import sys
import json
import requests
from typing import List
from constants import COLLECTION_TABLE_NAME, VEC_DIMENSION, OLLAMA_URL, LLM_MODEL
from getDatabase import getDatabase
from vectorize import vectorize


SYSTEM_PROMPT = """
First, assess whether the user's question is addressed or partially addressed by the search results.

If the search results contain information that is likely to help answer or clarify the question, even partially, treat it as relevant. 
Do not require an exact match of wording—conceptual relevance is sufficient.

Only if there is truly no meaningful or related information at all, respond:
"No relevant files were found." (translated into the same language with user's question).

If the information is relevant, generate a clear and concise answer in HTML format (not Markdown), using only the search results as your source. 
You may summarize, reorganize, or restate the relevant points to directly 
"""

K = 3

# --- SSE用コールバック ---
class SSECallbackHandler:
	def on_llm_new_token(self, token: str):
		# SSE形式で送信
		print(json.dumps({"token": token}), flush=True)

	def on_llm_end(self, response):
		# 終了を通知
		print("[DONE]", flush=True)


def retrieveSimilarDocs(query: str, k: int = 3):
	queryVec = vectorize(query)
	sql = f"""
		SELECT *, array_cosine_distance(embeddings, ?::FLOAT[{VEC_DIMENSION}]) AS similarity FROM {COLLECTION_TABLE_NAME} ORDER BY similarity DESC LIMIT {k}
	"""
	try:
		conn = getDatabase()
		results = conn.execute(sql, [queryVec]).fetchAll
	finally:
		conn.close()
	return [row["documents"] for row in results]  # documentsカラムだけ返す

def queryOllama(prompt: str, stream: bool = True, callbacks: List = None):
	url = f"{OLLAMA_URL}/v1/complete"
	data = {
		"model": LLM_MODEL,
		"prompt": prompt,
		"stream": stream,
		"temperature": 0,
		"num_ctx": 8192
	}
	if stream:
		with requests.post(url, json=data, stream=True) as r:
			for line in r.iter_lines():
				if line:
					tokenData = json.loads(line.decode("utf-8"))
					if callbacks:
						for cb in callbacks:
							cb.on_llm_new_token(tokenData.get("token", ""))
		if callbacks:
			for cb in callbacks:
				cb.on_llm_end(None)
	else:
		r = requests.post(url, json=data)
		return r.json()["completion"]

def runRag(userPrompt: str):
	# 1. 類似文書取得
	docs = retrieveSimilarDocs(userPrompt, k=K)
	context = "\n\n".join(docs)
	
	# 2. プロンプト作成
	fullPrompt = f"{SYSTEM_PROMPT}\n\n# User's Question:\n{userPrompt}\n\nSearch Results:\n{context}"
	
	# 3. LLM呼び出し
	sseHandler = SSECallbackHandler()
	queryOllama(fullPrompt, stream=True, callbacks=[sseHandler])

if __name__ == "__main__":
# --- 引数取得 ---
	userPrompt = sys.argv[1]
	runRag(userPrompt)
