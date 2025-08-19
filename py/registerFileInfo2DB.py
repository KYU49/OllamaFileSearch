from vectorize import vectorize
from pathlib import Path
from markitdown import MarkItDown
from extractous import Extractor, TesseractOcrConfig
import chardet

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