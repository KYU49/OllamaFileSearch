import sys
import io
import json
from constants import DB_PATH, COLLECTION_TABLE_NAME, VEC_DIMENSION
from vectorize import vectorize
from getDatabase import getDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

prompt = sys.argv[1]

embedding = vectorize(prompt)
conn = getDatabase()
queryVec = vectorize(prompt)
sql = f"""
	SELECT source, description, tags, array_cosine_distance(embeddings, ?::FLOAT[{VEC_DIMENSION}]) AS similarity FROM {COLLECTION_TABLE_NAME} ORDER BY similarity DESC LIMIT 20
"""
results = conn.execute(sql, [queryVec]).df()
conn.close()

# 検索
results["similarity"] = 1 - results["similarity"]

print(results)