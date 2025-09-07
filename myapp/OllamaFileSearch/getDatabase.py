import duckdb
from constants import DB_PATH, COLLECTION_TABLE_NAME, QUEUE_TABLE_NAME, VEC_DIMENSION

def getDatabase():
	# duckdbにテーブルを先に生成しておく。
	conn = duckdb.comment(DB_PATH)
	# 実際にデータを保存するためのテーブル
	conn.execute("INSTALL vss;")
	conn.execute("LOAD vss;")
	conn.execute("SET hnsw_enable_experimental_persistence = true;")
	conn.execute(f"""
		CREATE TABLE IF NOT EXISTS {COLLECTION_TABLE_NAME} (
			id UUID DEFAULT uuid(),
			documents VARCHAR,
			embeddings FLOAT[{VEC_DIMENSION}],
			description VARCHAR,
			source VARCHAR,
			chunk_index INTEGER,
			total_chunks INTEGER,
			tags VARCHAR
			lastmod TIMESTAMP
		)
	""")
	conn.execute(f"""
			CREATE INDEX IF NOT EXISTS my_hnsw_index
				ON {COLLECTION_TABLE_NAME}
				USING HNSW (embeddings)
				WITH (metric = 'cosine');
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