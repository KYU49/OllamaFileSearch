import duckdb
import os
from constants import DB_PATH, COLLECTION_TABLE_NAME, QUEUE_TABLE_NAME, VEC_DIMENSION

def getDatabase(readOnly = False):
	# duckdbにテーブルを先に生成しておく。
	conn = duckdb.connect(DB_PATH, read_only = readOnly)
	
	# --- 拡張機能の設定 ---
    # 拡張機能の保存先をプロジェクト内のフォルダに固定する（www-dataが書き込める場所）
	ext_dir = os.path.join(os.path.dirname(os.path.abspath(DB_PATH)), ".duckdb_extensions")
	os.makedirs(ext_dir, exist_ok=True)
	conn.execute(f"SET extension_directory = '{ext_dir}';")
	
	# 実際にデータを保存するためのテーブル
	try: 
		conn.execute("LOAD vss;")
	except Exception as e:
		if readOnly:
			raise RuntimeError(f"VSS extension not found in {ext_dir}. Run registration first.") from e
		# ロードに失敗した場合のみインストール（ダウンロード）を試みる
		try:
			conn.execute("INSTALL vss;")
			conn.execute("LOAD vss;")
		except Exception as e2:
			# ネットワークエラー等で失敗した場合は、詳細を表示して落とす
			raise RuntimeError(f"DuckDB 'vss' extension could not be loaded or installed: {e2}")

	if readOnly:
		return conn

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
			tags VARCHAR,
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