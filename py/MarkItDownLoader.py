from typing import List
import os
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from markitdown import MarkItDown

class MarkItDownLoader(BaseLoader):
	"""LangChain Custom Document Loader for Microsoft MarkItDown."""
	
	def __init__(self, file_path: str):
		if not os.path.exists(file_path):
			raise FileNotFoundError(f"File not found: {file_path}")
		self.file_path = file_path

	def load(self) -> List[Document]:
		"""同期的にファイルを読み込み、LangChainのDocument形式で返す"""
		# MarkItDownでファイルを読み込む
		md = MarkItDown(self.file_path)
		text = md.get_text()  # get_text() でテキスト抽出
		
		# Documentに変換
		return [Document(page_content=text, metadata={"source": self.file_path})]

	async def aload(self) -> List[Document]:
		"""非同期読み込み"""
		return self.load()