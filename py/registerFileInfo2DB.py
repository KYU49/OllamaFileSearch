from pathlib import Path
import yaml
from vectorize import vectorize
from markitdown import MarkItDown
from extractous import Extractor, TesseractOcrConfig
import chardet
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector

# MicrosoftのMarkItDown版。
def getFileText(filePath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	match ext:
		case ".txt" | ".md":
			text = ""
			# 文字コードの判定
			with open(filePath, "rb") as file:
				raw_data = file.read()
				result = chardet.detect(raw_data)
				encoding = result["encoding"]
			# 判定した文字コードで開く
			with open(filePath, "r", encoding=encoding) as file:
				text = file.read()
			return text
		case ".docx" | ".xlsx" | ".pptx" | ".pdf":
			md = MarkItDown(enable_plugins=False)
			result = md.convert(filePath)
			return result.text_content
	return ""

# OCRにはtesseract-ocrが必要。
def getFileTextEx(filePath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()
	match ext:
		case ".png" | ".jpeg" | ".tiff" | ".bmp" | ".gif" | ".svg":
			# `sudo apt install tesseract-ocr tesseract-ocr-jpn`
			extractor = Extractor().set_ocr_config(TesseractOcrConfig().set_language("jpn"))
			result, metadata = extractor.extract_file_to_string(filePath)
			return result
		case ".docx" | ".doc" | ".xlsx" | ".xls" | ".pptx" | ".ppt" | ".pdf" | ".tsv" | ".csv" | ".html" | ".txt" | ".md":
			extractor = Extractor()
			result, metadata = extractor.extract_file_to_string(filePath)
			return result
	return ""

def db_cos_sim_search(queryVec):
	with open("../.config/secret.yaml", "r") as f:
		secrets = yaml.safe_load(f)
	with psycopg2.connect(f"dbname={secrets["db_name"]} user={secrets["db_user"]} password={secrets["db_pass"]} host={secrets["db_host"]} port={secrets["db_port"]}") as con:
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
	with psycopg2.connect(f"dbname={secrets["db_name"]} user={secrets["db_user"]} password={secrets["db_pass"]} host={secrets["db_host"]} port={secrets["db_port"]}") as con:
		register_vector(con)
		with con.cursor() as c:
			execute_values(c, 
				f"INSERT INTO tbl (filePath, text, description, label, lastModified, queryVec) VALUES %s ON CONFLICT DO NOTHING", 
				data,
				"(%s, %s, %s, %s, %s, %s, CAST(%s AS VECTOR(768)))"
			)
			con.commit()

def detect(file = ""):
	# 内部テキストの変更がなければ、フラグなどのみ編集

	# ファイル内容をテキストとして取得
	text = getFileText(file)
	print(text)	#FIXME	
	# ファイル内容を登録するために、Vectorを取得
	#vector = vectorize(text)
	
	# ファイル内容の簡単な説明をLLMで作成

	# ファイルにscikit-Ollamaでラベル付け

	# 変更があったファイルについて、変更の種類によって場合分けし、変更をDBに反映するSQLを生成

	# SQLに反映

def main():
	detect("../.test/test.pdf")

if __name__ == "__main__":
	main()

#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 