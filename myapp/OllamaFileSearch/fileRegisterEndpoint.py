import sys
import os
import re
import time
from datetime import datetime
from getFileText import getFileText
from constants import COLLECTION_TABLE_NAME, QUEUE_TABLE_NAME, LOCK_FILE
from getDatabase import getDatabase
from vectorize import vectorize
from promptOllama import summarize4description, labeling

try: 
	import fcntl
except ImportError:
	import fctrl_win as fcntl

MAX_RETRIES = 3
SLEEP_INTERVAL = 5

# sys.argv[1]: ファイルパス; [2]: 変更内容(added/modified/deleted/unknown)

#TODO https://voluntas.ghost.io/duckdb-japanese-full-text-search/ を参考に、DuckDBを用いた、全文検索に変更。hybrid検索はこっちも参照。https://voluntas.ghost.io/duckdb-hybrid-search/
def enqueueJob(filePath, action):
	conn = getDatabase()
	# 削除イベントはキューに乗せない
	if action == "deleted":
		source = re.sub(r"^.*?OllamaFileSearch/files", r"files", filePath)
		conn.execute(f"DETETE FROM {COLLECTION_TABLE_NAME} WHERE source = ?", [source])
		return
	
	priority_map = {"added": 1, "modified": 2}
	priority = priority_map.get(action, 3)

	conn.execute(f"INSERT INTO {QUEUE_TABLE_NAME} (file_path, action, status, retry_count, timestamp, error) VALUES (?, ?, 'pending', 0, ?, '')", [filePath, action, datetime.now()])
	conn.close()
	workerLoop()

def reregisterAll(path = "/var/www/html/OllamaFileSearch/files"):
	conn = getDatabase()
	for filePath in os.listdir(path):
		conn.execute(f"INSERT INTO {QUEUE_TABLE_NAME} (file_path, action, status, retry_count, timestamp, error) VALUES (?, 'modified', 'pending', 0, ?, '')", [filePath, datetime.now()])
	conn.close()
	workerLoop()


def workerLoop():
	# flock で排他ロックを確保
	os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
	with open(LOCK_FILE, "w") as lockfile:
		try:
			fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except BlockingIOError:
			return  # 他プロセスが実行中なら終了
		
		conn = getDatabase()

		while True:
			jobs = conn.execute(f"SELECT id, file_path, retry_count, timestamp FROM {QUEUE_TABLE_NAME} WHERE status = 'pending' ORDER BY timestamp ASC LIMIT 1").fetchall()
			if not jobs:
				return
			jobId, filePath, retryCount, timestamp = jobs[0]
			# 実行中のジョブをブロック
			conn.execute(f"UPDATE {QUEUE_TABLE_NAME} SET status = 'processing' WHERE id = ?", [jobId])

			try:
				if not filePath or not os.path.isfile(filePath):
					conn.execute(f"DELETE FROM {QUEUE_TABLE_NAME} WHERE id = ?", [jobId])
					continue

				# ファイル読み込み
				text = getFileText(filePath)
				
				# Moder BertのToken数が8192 (8192 * 0.96 = 7864.32文字)のため、分割する
				chunkSize = 6000
				overlap = 200
				chunks = [text[i:i + chunkSize] for i in range(0, len(text), chunkSize - overlap)]

				# sourceには/var/www/html/OllamaFileSearchからの相対パスを入れたいため、filePathを加工
				source = re.sub(r"^.*?OllamaFileSearch/files", "files", filePath)

				# 既にあったら削除しておく(modifiedの場合だけでいいんだけど、処理しちゃったほうが早い)
				conn.execute(f"DELETE FROM {COLLECTION_TABLE_NAME} WHERE source = ? ", [source])

				# 挿入
				description = ""
				tags = "[]"
				for i, chunk in enumerate(chunks):
					embedding = vectorize(chunk)
					if i == 0:
						beginning = text[:5000]	# 文字数が溢れないように最初だけをLLMに投げる
						description = summarize4description(beginning)
						tags = labeling(beginning)
					conn.execute(f"""
						INSERT INTO {COLLECTION_TABLE_NAME} (documents, embeddings, description, source, chunk_index, total_chunks, tags, lastmod)
						VALUES (?, ?, ?, ?, ?, ?, ?, ?)
					""", [chunk, embedding, description, source, i, len(chunks), tags, datetime.now()])

				# ジョブ削除
				conn.execute(f"DELETE FROM {QUEUE_TABLE_NAME} WHERE id = ?", [jobId])

			except Exception as e:
				print(e)
				if retryCount >= MAX_RETRIES:
					conn.execute(f"""
						UPDATE {QUEUE_TABLE_NAME}
						SET status = 'failed', error = ?, retry_count = ?
						WHERE id = ?
					""", [str(e), retryCount, jobId])
					retryCount = 0
				else:
					conn.execute(f"""
						UPDATE {QUEUE_TABLE_NAME}
						SET status = 'pending', retry_count = ?, error = ?
						WHERE id = ?
					""", [retryCount + 1, str(e), jobId])
			time.sleep(SLEEP_INTERVAL * (2 ** retryCount))

if __name__ == "__main__":
	if len(sys.argv) < 3:
		if len(sys.argv) == 2 and sys.argv[1] == "all":
			reregisterAll()
		print("Usage: enqueue_job.py <file_path> <action>")
		sys.exit(1)

	enqueueJob(sys.argv[1], sys.argv[2])

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 