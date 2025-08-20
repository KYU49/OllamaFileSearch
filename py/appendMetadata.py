import os
from promptOllama import summarize4description, labeling

# 文書の序盤からメタデータを作成。
def appendMetadata(doc):
	text = doc.page_content
	beginning = text[:3000]	# 文字数が溢れないように最初だけをLLMに投げる
	description = summarize4description(beginning)
	label = labeling(beginning)

	doc.metadata.update({
		"description": description,
		"label": label,
		"last_modified": os.path.getmtime(doc.metadata["source"]),
	})
	return doc


#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 