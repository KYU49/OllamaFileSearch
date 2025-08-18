import torch
from transformers import AutoTokenizer, AutoModel, pipeline
import numpy as np

# # Requirements
# uv add flash-attn --no-build-isolation
# uv add protobuf
# uv add sentencepiece

def vectorize(text):
	# BERTトークナイザーのロード
	tokenizer = AutoTokenizer.from_pretrained("sbintuitions/modernbert-ja-310m", torch_dtype=torch.bfloat16)
	# BERTモデルのロード
	model = AutoModel.from_pretrained("sbintuitions/modernbert-ja-310m", torch_dtype=torch.bfloat16)
	extractor = pipeline(model=model, task = "feature-extraction", tokenizer = tokenizer)

	# BERTでベクトル化
	features = extractor(text)
	token_vectors = features[0]
	cls_vector = np.mean(token_vectors, axis=0)
	
	return cls_vector

def cos_sim(v1, v2):
	return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


# This software includes code licensed under the MIT License.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
