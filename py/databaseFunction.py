import yaml
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

def db_cos_sim_search(queryVec):
	with open("../.config/secret.yaml", "r") as f:
		secrets = yaml.safe_load(f)
	with psycopg2.connect(f"dbname={secrets['db_name']} user={secrets['db_user']} password={secrets['db_pass']} host={secrets['db_host']} port={secrets['db_port']}") as con:
		register_vector(con)
		with con.cursor() as c:
			c.execute("SELECT * FROM tbl ORDER BY vec <=> %s LIMIT 100", (queryVec, ))
			return c.fetchall()


def db_insert(filePath, text, description, label, lastModified, queryVec):
	with open("../.config/secret.yaml", "r") as f:
		secrets = yaml.safe_load(f)
	# Bulk Insertに対応するためにzipにしてるけど、基本的には不要。
	data = list(zip(
		[filePath], 
		[text],
		[description],
		[label],
		[lastModified],
		[queryVec]
	))
	with psycopg2.connect(f"dbname={secrets['db_name']} user={secrets['db_user']} password={secrets['db_pass']} host={secrets['db_host']} port={secrets['db_port']}") as con:
		register_vector(con)
		with con.cursor() as c:
			execute_values(c, 
				f"INSERT INTO tbl (filePath, text, description, label, lastModified, queryVec) VALUES %s ON CONFLICT DO NOTHING", 
				data,
				"(%s, %s, %s, %s, %s, %s, CAST(%s AS VECTOR(768)))"
			)
			con.commit()