from pathlib import Path
from markitdown import MarkItDown
from extractous import Extractor, TesseractOcrConfig
from langchain_community.document_loaders import PyPDFium2Loader, BSHTMLLoader
from langchain_community.document_loaders.text import TextLoader
import chardet

# Langchain版
def getFileText(filaPath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	# 参考: https://zenn.dev/chips0711/articles/25c11940a999a1

	match ext:
		case ".txt" | ".md":
		case ".html":
		case ".docx" | ".xlsx" | ".pptx":
		case ".pdf":
	return ""


# MicrosoftのMarkItDown版。
def getFileTextMID(filePath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	match ext:
		case ".txt" | ".md" | ".html":
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