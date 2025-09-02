
class DummyEmbeddings:
	def __init__(self, dim: int = 1):
		self.dim = dim
	def embed_documents(self, texts):
		# texts の数だけ dim 長のゼロベクトルリストを返す
		return [[0.0] * self.dim for _ in texts]
	def embed_query(self, text):
		return [0.0] * self.dim
	