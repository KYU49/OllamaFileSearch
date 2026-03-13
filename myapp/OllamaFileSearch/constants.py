import os

# LLM_MODEL = "gpt-oss:20b"
LLM_MODEL = "qwen3.5:9B"
# EMBEDDING_MODEL = "sbintuitions/modernbert-ja-310m"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-4B"
IS_QWEN = True
PY_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = PY_SCRIPT_PATH + "/.cache"
DB_PATH = PY_SCRIPT_PATH  + "/ofs.duckdb"
COLLECTION_TABLE_NAME = "ollama_file_table"
QUEUE_TABLE_NAME = "queue_table"
LOCK_FILE = CACHE_PATH + "/fileRegisterQueueLoop.lock"
YAML_PATH = "/var/www/html/OllamaFileSearch/.config/labelList.yaml"
OLLAMA_URL = "http://localhost:11434"
MAX_CONTEXT = 8192	 # gpt-oss:20bなら8192
# VEC_DIMENSION = 768	# MODERNBERT-ja-310mなら
VEC_DIMENSION = 2560
UNCATEGORIZED_LABEL = "未分類"