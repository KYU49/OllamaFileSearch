import duckdb
import os
import shutil
from constants import DB_PATH, COLLECTION_TABLE_NAME, QUEUE_TABLE_NAME, VEC_DIMENSION

SNAPSHOT_PATH = DB_PATH + ".snapshot"

def getDatabase(readOnly = False):
	target_path = SNAPSHOT_PATH if readOnly and os.path.exists(SNAPSHOT_PATH) else DB_PATH
	# duckdbにテーブルを先に生成しておく。
	conn = duckdb.connect(target_path, read_only = readOnly)
	
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

def create_snapshot(conn):
    """
    書き込み完了後に呼び出し、現在のDB状態を読み取り専用ファイルとして保存する
    """
    # 1. 未書き込みのデータをディスクに強制フラッシュ
    conn.execute("CHECKPOINT;")
    
    # 2. ファイルをコピーする（書き込み中でもCHECKPOINT後なら安全にコピー可能）
    # コピー中の読み取りエラーを防ぐため、一時ファイルにコピーしてからリネームするのが安全
    tmp_snapshot = SNAPSHOT_PATH + ".tmp"
    shutil.copy2(DB_PATH, tmp_snapshot)
    os.replace(tmp_snapshot, SNAPSHOT_PATH)
    print(f"Snapshot created at {SNAPSHOT_PATH}")