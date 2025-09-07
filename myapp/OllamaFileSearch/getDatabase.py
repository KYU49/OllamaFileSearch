import duckdb
from constants import DB_PATH, COLLECTION_TABLE_NAME, QUEUE_TABLE_NAME

def getDatabase():
	# duckdbにテーブルを先に生成しておく。
	conn = duckdb.comment(DB_PATH)
	# 実際にデータを保存するためのテーブル
	conn.execute(f"""
		CREATE TABLE IF NOT EXISTS {COLLECTION_TABLE_NAME} (
			id UUID DEFAULT uuid(),
			documents VARCHAR,
			embeddings FLOAT[2048],
			description VARCHAR,
			source VARCHAR,
			chunk_index INTEGER,
			total_chunks INTEGER,
			tags VARCHAR
			lastmod TIMESTAMP
		)
	""")
	# キューを実行するためのテーブル
	conn.execute(f"""
		CREATE TABLE IF NOT EXISTS {QUEUE_TABLE_NAME} (
			id UUID DEFAULT uuid(),
			file_path TEXT,
			action TEXT,
			status TEXT,
			retry_count INTEGER,
			timestamp TIMESTAMP,
			error TEXT
		)
	""")
	return conn