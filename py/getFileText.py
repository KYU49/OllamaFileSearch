from enum import Enum
from pathlib import Path
from langchain_core.documents import Document

# Langchain版 参考: https://note.com/jolly_azalea818/n/n763880f1668a
class Method(Enum):
	LANG_CHAIN = 1
	MARK_IT_DOWN = 2
	EXTRACTOUS = 3

# 基本はこれを呼び出す。listではなく、まとめて返す。
def getFileText(filePath: str, methodType=Method.LANG_CHAIN):
	match methodType:
		case Method.LANG_CHAIN:
			func = getFileTextLangChain
		case Method.MARK_IT_DOWN:
			func = getFileTextMID
		case Method.EXTRACTOUS:
			func = getFileTextEx
		case _:
			return None
	docs = func(filePath)

	# ページ内容を結合
	fullText = "\n".join(doc.page_content for doc in docs)
	
	# メタデータは最初のドキュメントからコピー（必要に応じて調整可能）
	mergedMetadata = docs[0].metadata.copy()
	
	# 新しい Document として結合
	mergedDoc = Document(
		page_content=fullText,
		metadata=mergedMetadata
	)
	return mergedDoc



def getFileTextLangChain(filePath: str):
	import MarkItDownLoader
	from langchain_community.document_loaders import PyPDFium2Loader, BSHTMLLoader
	from langchain_community.document_loaders.text import TextLoader

	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	# 参考: https://zenn.dev/chips0711/articles/25c11940a999a1

	match ext:
		case ".txt" | ".md":
			return TextLoader(filePath, autodetect_encoding=True).load()
		case ".html":
			return BSHTMLLoader(filePath).load()
		case ".docx" | ".xlsx" | ".pptx" | ".msg":
			return MarkItDownLoader(filePath).load()
		case ".pdf":
			return PyPDFium2Loader(filePath).load()
	return []


# MicrosoftのMarkItDown版。
def getFileTextMID(filePath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	match ext:
		case ".txt" | ".md" | ".html":
			import chardet
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
			from markitdown import MarkItDown

			md = MarkItDown(enable_plugins=False)
			result = md.convert(filePath)
			return result.text_content
	return ""

# OCRにはtesseract-ocrが必要。
def getFileTextEx(filePath: str):
	from extractous import Extractor, TesseractOcrConfig
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