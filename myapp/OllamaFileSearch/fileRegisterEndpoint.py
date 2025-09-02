import sys
import os
import time
from datetime import datetime
from getFileText import getFileText
from appendMetadata import appendMetadata
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from ModernBertEmbeddings import ModernBERTEmbeddings
from DummyEmbeddings import DummyEmbeddings
from constants import DB_PATH, COLLECTION_NAME, LOCK_FILE
try: 
	import fcntl
except ImportError:
	import fctrl_win as fcntl

JOB_COLLECTION = "file_jobs"
MAX_RETRIES = 3
SLEEP_INTERVAL = 5

# sys.argv[1]: ファイルパス; [2]: 変更内容(added/modified/deleted/unknown)

def enqueueJob(filePath, action):
	# 削除イベントはキューに乗せない
	if action == "deleted":
		db = Chroma(persist_directory=DB_PATH, collection_name=COLLECTION_NAME, embedding_function=DummyEmbeddings())	# こっちは削除用だからdocの入っているdb
		id2delete = db.get(where={"source": filePath})
		if len(id2delete.get("ids")) > 0:
			db.delete(ids = id2delete.get("ids"))
		return
	
	priority_map = {"added": 1, "modified": 2}
	priority = priority_map.get(action, 3)
	db = Chroma(persist_directory=DB_PATH, collection_name=JOB_COLLECTION, embedding_function=DummyEmbeddings())
	db.add_texts(
		texts=[""],
		metadatas = [{
			"filePath": filePath,
			"action": action,
			"status": "pending",
			"retryCount": 0,
			"priority": priority,
			"timestamp": datetime.now().isoformat()
		}]
	)

	workerLoop()

def workerLoop():
	# flock で排他ロックを確保
	os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
	with open(LOCK_FILE, "w") as lockfile:
		try:
			fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except BlockingIOError:
			return  # 他プロセスが実行中なら終了

		embeddings = ModernBERTEmbeddings()
		dbJob = Chroma(persist_directory=DB_PATH, collection_name=JOB_COLLECTION, embedding_function=DummyEmbeddings())
		db = Chroma(
			persist_directory=DB_PATH,
			embedding_function=embeddings,
			collection_name=COLLECTION_NAME,
			collection_metadata={"hnsw:space": "cosine"},
		)
		while True:
			jobs = dbJob.get(where = {"status": "pending"})
			if not jobs["ids"]:
				return
			
			sortedJobs = sorted(
				zip(jobs["ids"], jobs["metadatas"]),
				key = lambda x: (x[1].get("priority", 3), x[1].get("timestamp", ""))
			)
			jobId, metadata = sortedJobs[0]
			filePath = metadata["filePath"]
			# action = metadata["action"]	# delete以外はpriorityにしか使わないから、多分不要
			retryCount = metadata.get("retryCount", 0)

			dbJob.delete(ids=[jobId])
			processingIds = dbJob.add_texts(
				texts=[""],
				metadatas=[{**metadata, "status": "processing"}]
			)

			try:
				if (not filePath) or (not os.path.isfile(filePath)):
					continue
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

				# 同じ文書由来のものを検索する際に、1つ目 (or 2つ目移行がヒットするなら最初)だけを表示するため。
				for i, chunk in enumerate(docs):
					chunk.metadata["chunk_index"] = i
				# 既にあったら削除しておく(modifiedの場合だけでいいんだけど、処理しちゃったほうが早い)
				for d in docs:
					source = d.metadata.get("source")
					if source:
						id2delete = db.get(where={"source": source})
						if len(id2delete.get("ids")) > 0:
							db.delete(ids = id2delete.get("ids"))
				# 実際のinsert
				db.add_documents(docs)
				# 成功したらジョブは削除
				dbJob.delete(ids=processingIds)
			except Exception as e:
				print("Database registration error: ", e)
				dbJob.delete(ids=processingIds)
				retryCount += 1
				if retryCount >= MAX_RETRIES:
					dbJob.add_texts(
						texts=[""],
						metadatas=[{**metadata, "status": "failed", "error": str(e), "retryCount": retryCount}]
					)
					retryCount = 0
				else:
					dbJob.add_texts(
						texts=[""],
						metadatas=[{**metadata, "status": "pending", "retryCount": retryCount, "error": str(e)}]
					)
			time.sleep(SLEEP_INTERVAL * (2 ** (retryCount - 1)))

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: enqueue_job.py <file_path> <action>")
		sys.exit(1)

	enqueueJob(sys.argv[1], sys.argv[2])

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 