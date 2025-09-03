import re
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class PageContentRetrieverWrapper(BaseRetriever):
	"""
	元のretrieverをラップして、Document.metadataを空にする
	RetrievalQA.from_chain_typeで利用可能
	"""
	retriever: BaseRetriever

	def _get_relevant_documents(self, query: str) -> List[Document]:
		docs = self.retriever.invoke(query)
		return [Document(page_content=getattr(doc, "page_content", getattr(doc, "documents", "")), metadata={}) for doc in docs]
	
	async def _aget_relevant_documents(self, query: str):
		docs = await self.retriever.ainvoke(query)
		return [Document(page_content=getattr(doc, "page_content", getattr(doc, "documents", "")), metadata={}) for doc in docs]