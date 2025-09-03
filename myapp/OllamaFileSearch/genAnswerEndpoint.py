import sys
import json
from langchain_ollama import OllamaLLM
from langchain.chains import create_retrieval_chain
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings
from constants import DB_PATH, COLLECTION_NAME


SYSTEM_PROMPT = """
# Order
First, assess whether the user's question is addressed or partially addressed by the search results.

If the search results contain information that is likely to help answer or clarify the question, even partially, treat it as relevant. 
Do not require an exact match of wording—conceptual relevance is sufficient.

Only if there is truly no meaningful or related information at all, respond:
"No relevant files were found." (translated into the same language with user's question).

If the information is relevant, generate a clear and concise answer in HTML format (not Markdown), using only the search results as your source. 
You may summarize, reorganize, or restate the relevant points to directly 

# Search Results
{context}

# User's Question
{question}
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
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})


llm = OllamaLLM(
	model="gpt-oss:20b", 
	base_url="http://localhost:11434", 
	streaming=True, 
	temperature=0,
	num_ctx=8192	# 8192で14GBくらいになる
)

prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

def formatDocs(docs):
    return "\n\n".join(
        getattr(doc, "page_content", getattr(doc, "documents", "")) 
        for doc in docs
    )

chainRagFromDocs = (
	RunnablePassthrough.assign(content=(lambda x: formatDocs(x["context"])))
	| prompt
	| llm
)
chainWithRag = RunnableParallel(
	{"context": retriever, "question": RunnablePassthrough()}
).assign(answer = chainRagFromDocs)


# --- SSE用コールバック ---
class SSECallbackHandler(BaseCallbackHandler):
	def on_llm_new_token(self, token: str, **kwargs):
		# SSE形式で送信
		print(json.dumps({"token": token}), flush=True)

	def on_llm_end(self, response, **kwargs):
		# 終了を通知
		print("[DONE]", flush=True)

for chunk in chainWithRag.stream(userPrompt, config={"callbacks": [SSECallbackHandler()]}):
	pass	# SSEは逐次コールバックで送信されるのでここでは何もしない

