import os
import yaml
import requests
from constants import OLLAMA_URL, LLM_MODEL, UNCATEGORIZED_LABEL, YAML_PATH

SUMMARY_PROMPT = """
You are a concise description generator.
Given an input text extracted from a file, generate a summary in Japanese of around 100 characters that clearly explains the file's content and purpose.
Output only the summary text, without any labels, extra words, or formatting.

# Input Text

"""

LABELING_PROMPT = """
Classify the following passage into one of the predefined labels.
Output a single label name only.

Predefined labels:
{labels}

Passage:
{input}
"""

os.environ["NO_PROXY"] = "localhost,127.0.0.1"


def summarize4description(text):
	
	#url = f"{OLLAMA_URL}/v1/models/{LLM_MODEL}/generate"
	url = f"{OLLAMA_URL}/api/generate"
	headers = {
		"Content-Type": "application/json",
	}
	payload = {
		"model": LLM_MODEL,
		"prompt": SUMMARY_PROMPT + text,
		"stream": False,
		"temperature": 0,
		"max_context": 8192
	}

	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()  # エラーがあれば例外を発生させる

	data = response.json()
	# Ollamaのレスポンス形式に応じて以下を調整
	return data.get("response", "")  # 例: "result"キーに生成テキストが入る場合

def labeling(text):
	tagging_prompt = ChatPromptTemplate.from_template(LABELING_PROMPT)
	llm = OllamaLLM(model=LLM_MODEL, base_url=OLLAMA_URL)
	prompt = tagging_prompt.format(input=text, labels=", ".join(loadLabels()))
	return llm.invoke(prompt)

def loadLabels():
	try:
		with open(YAML_PATH, "r", encoding="utf-8") as f:
			labels = yaml.safe_load(f)
			if isinstance(labels, dict):
				labels = list(labels.values())
			return labels
	except FileNotFoundError:
		return [UNCATEGORIZED_LABEL]

	
