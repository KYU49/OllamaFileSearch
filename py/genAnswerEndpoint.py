import os
import sys
from langchain_ollama import OllamaLLM
from langchain.chains import create_retrieval_chain
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings

STORE_PATH = os.getcwd() + "/chromadb"
COLLECTION_NAME = "ollama_file_collection"

SYSTEM_PROMPT = """
# Order
First, determine whether the user's question is relevant to the search results.

If the relevance is low or there is no meaningful connection, respond in the same language as the user's question with a phrase meaning:
"No relevant information was found in the search results."

Only if the question is relevant, generate an answer based solely on the provided search results.
Do not use any external knowledge outside of the search results.

# Search Results
{context}

# User's Question
{question}
"""

# --- 引数取得 ---
userPrompt = sys.argv[1]

embeddings = ModernBERTEmbeddings()
db = Chroma(
	persist_directory=STORE_PATH,
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
    num_ctx=8192    # 8192で14GBくらいになる
)

prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

def formatDocs(docs):
    return "\n\n".join(
        doc.page_content for doc in docs
    )

chainRagFromDocs = (
    RunnablePassthrough.assign(content=(lambda x: formatDocs(x["context"])))
    | prompt
    | llm
)
chainWithRag = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer = chainRagFromDocs)

answer = chainWithRag.invoke(userPrompt)

respTemplate = PromptTemplate.from_template("""
answer: {answer}
source: {source}
""")

resp = respTemplate.invoke({
    "answer": answer["answer"],
    "source": answer["context"][0].metadata["source"]
})

print(resp.text)

if(False):

    qa_chain = create_retrieval_chain(llm, promptTemplate)
    chain = create_retrieval_chain(retriever, qa_chain)

    # --- コールバックでトークン逐次出力 ---

    # CallbackHandlerで逐次結果を処理
    class StreamCallbackHandler(BaseCallbackHandler):
        def __init__(self):
            self.output = []

        def on_llm_new_token(self, token: str, **kwargs):
            # 新しいトークンを受け取るたびに呼ばれる
            self.output.append(token)
            # 現在のトークンを逐次的にPHPに返す
            sys.stdout.write(token)  # PHPにリアルタイムで返す
            sys.stdout.flush()  # バッファを即時出力
        # コンテキストマネージャ用のメソッドを追加
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_value, traceback):
            # エラー処理を適切に行いたい場合はここで
            pass

    # CallbackHandlerのインスタンス化
    callback_handler = StreamCallbackHandler()

    # 結果を逐次的に出力
    with callback_handler:
        result = chain.call(input=prompt)

    # 最後の結果を出力
    print("\n".join(callback_handler.output))
