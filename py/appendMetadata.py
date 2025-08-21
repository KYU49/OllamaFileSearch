import os
from promptOllama import summarize4description, labeling
from datetime import datetime

# 文書の序盤からメタデータを作成。
def appendMetadata(doc):
	text = doc.page_content
	beginning = text[:3000]	# 文字数が溢れないように最初だけをLLMに投げる
	description = summarize4description(beginning)
	label = labeling(beginning)
	dt = datetime
	timestamp = os.path.getmtime(doc.metadata["source"])
	dt = datetime.fromtimestamp(timestamp)
	doc.metadata.update({
		"description": description,
		"label": label,
		"last_modified": dt.isoformat(),	# 2025-08-21T12:34:56.123456のようになるはず。
	})
	return doc


#
# This code uses the following MIT-licensed library:
# * License: MIT License (Details: https://opensource.org/licenses/MIT)
# - MarkItDown https://github.com/microsoft/markitdown
# 