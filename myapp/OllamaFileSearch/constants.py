import os

LLM_MODEL = "gpt-oss:20b"
BERT_MODEL = "sbintuitions/modernbert-ja-310m"
PY_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = PY_SCRIPT_PATH + "/.cache"
DB_PATH = PY_SCRIPT_PATH  + "/chromadb"
COLLECTION_NAME = "ollama_file_collection"
LOCK_FILE = CACHE_PATH + "/fileRegisterQueueLoop.lock"
YAML_PATH = "/var/www/html/OllamaFileSearch/.config/labelList.yaml"
OLLAMA_URL = "http://localhost:11434"
UNCATEGORIZED_LABEL = "未分類"