import os
import yaml
import requests
import json
from constants import OLLAMA_URL, LLM_MODEL, UNCATEGORIZED_LABEL, YAML_PATH

os.environ["NO_PROXY"] = "localhost,127.0.0.1"


def summarize4description(text):
	url = f"{OLLAMA_URL}/api/generate"
	headers = {
		"Content-Type": "application/json",
	}

	SUMMARY_PROMPT = f"""
You are a concise description generator.
Given an input text extracted from a file, generate a summary in Japanese of around 100 characters that clearly explains the file's content and purpose.
Output only the summary text, without any labels, extra words, or formatting.

# Input Text
{text}
"""
	payload = {
		"model": LLM_MODEL,
		"prompt": SUMMARY_PROMPT,
		"stream": False,
		"temperature": 0,
		"max_context": 8192
	}

	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()  # エラーがあれば例外を発生させる

	data = response.json()
	# Ollamaのレスポンス形式に応じて以下を調整
	return data.get("response", "")

def labeling(text):
	url = f"{OLLAMA_URL}/api/generate"
	headers = {
		"Content-Type": "application/json",
	}
	labels = ", ".join(loadLabels())
	LABELING_PROMPT = f"""
Classify the following passage into one or more of the predefined labels.
Output the result as a JSON array of label names.

Predefined labels:
{labels}

Passage:
{text}
"""
	payload = {
		"model": LLM_MODEL,
		"prompt": LABELING_PROMPT,
		"stream": False,
		"temperature": 0,
		"max_context": 8192
	}

	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()  # エラーがあれば例外を発生させる

	data = response.json()
	return data.get("response", "")


def loadLabels():
	try:
		with open(YAML_PATH, "r", encoding="utf-8") as f:
			labels = yaml.safe_load(f)
			if isinstance(labels, dict):
				labels = list(labels.values())
			return labels
	except FileNotFoundError:
		return [UNCATEGORIZED_LABEL]

	
