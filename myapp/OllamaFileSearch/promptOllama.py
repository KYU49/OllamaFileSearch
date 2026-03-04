import os
import sys
import yaml
import requests
import json
from constants import OLLAMA_URL, LLM_MODEL, UNCATEGORIZED_LABEL, YAML_PATH, MAX_CONTEXT

os.environ["NO_PROXY"] = "localhost,127.0.0.1"


def summarize4description(text):
	url = f"{OLLAMA_URL}/api/generate"
	headers = {
		"Content-Type": "application/json",
	}

	SUMMARY_PROMPT = f"""<|im_start|>system
You are a concise description generator.
Given an input text extracted from a file, generate a summary in Japanese of around 200 characters that clearly explains the file's content and purpose.
Output only the summary text, without any labels, extra words, or formatting.<|im_end|>
<|im_start|>user
# Input Text
{text}
<|im_end|>
<|im_start|>assistant
"""
	payload = {
		"model": LLM_MODEL,
		"prompt": SUMMARY_PROMPT,
		"stream": False,
		"options": {
			"num_predict": -1,
			"temperature": 0.3,
			"top_p": 0.9,
			"num_gpu": 99,
			"num_context": MAX_CONTEXT
		}
	}

	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()  # エラーがあれば例外を発生させる

	data = response.json()
	# Ollamaのレスポンス形式に応じて以下を調整
	return data.get("response", "").strip()

def labeling(text):
	url = f"{OLLAMA_URL}/api/generate"
	headers = {
		"Content-Type": "application/json",
	}
	labels = ", ".join(loadLabels())
	LABELING_PROMPT = f"""<|im_start|>system
Classify the following passage into one or more of the predefined labels.
Output the result as a JSON array of label names.

# Predefined labels
{labels}<|im_end|>
<|im_start|>user
# Passage
{text}
<|im_end|>
<|im_start|>assistant
"""
	payload = {
		"model": LLM_MODEL,
		"prompt": LABELING_PROMPT,
		"stream": False,
		"format": "json",
		"options": {
			"num_predict": -1,
			"temperature": 0,
			"num_gpu": 99,
			"num_context": MAX_CONTEXT
		}
	}

	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()  # エラーがあれば例外を発生させる

	data = response.json()
	return data.get("response", "").strip()


def loadLabels():
	try:
		with open(YAML_PATH, "r", encoding="utf-8") as f:
			labels = yaml.safe_load(f)
			if isinstance(labels, dict):
				labels = list(labels.values())
			return labels
	except FileNotFoundError:
		return [UNCATEGORIZED_LABEL]

	
# テスト用
if __name__ == "__main__":
    # 引数があればそれを使い、なければ標準入力から読み込む
    if len(sys.argv) > 1:
        test_text = sys.argv[1]
    else:
        print("要約させるテキストを入力 (Ctrl + Dで確定):")
        test_text = sys.stdin.read()

    if not test_text.strip():
        print("テキストが空です。")
        sys.exit(1)

    print("\n" + "="*30)
    print("要約テスト実行中...")
    summary = summarize4description(test_text)
    print(f"結果:\n{summary}")

    print("\n" + "="*30)
    print("ラベル付けテスト実行中...")
    labels = labeling(test_text)
    print(f"結果:\n{labels}")
    print("="*30)