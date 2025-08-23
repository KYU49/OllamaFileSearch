import sys
import json
from langchain_chroma.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.callbacks.base import BaseCallbackHandler

# --- 引数取得 ---
search_results = json.loads(sys.argv[1])  # PHP側で渡された検索結果
prompt = sys.argv[2]

# --- Chromaベクトルストア準備 ---
persist_directory = "./chroma.db"
embedding_model = HuggingFaceEmbeddings(
	model_name="sbintuitions/modernbert-ja-310m"
)
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# --- Ollama LLM（ローカルモデル） ---
# streaming=True を使うと逐次トークンコールバック可能
llm = OllamaLLM(model="gpt-oss:20b", streaming=True, temperature=0)

# --- コールバックでトークン逐次出力 ---
class StreamingCallbackHandler(BaseCallbackHandler):
	def on_llm_new_token(self, token: str, **kwargs):
		print(token, flush=True)  # PHP SSEに逐次送信

handler = StreamingCallbackHandler()

# --- RetrievalQAチェーン作成 ---
qa_chain = RetrievalQA.from_chain_type(
	llm=llm,
	chain_type="stuff",
	retriever=retriever,
	return_source_documents=False
)

# --- 回答生成 ---
qa_chain.run(prompt, callbacks=[handler])