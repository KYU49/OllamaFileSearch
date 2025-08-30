import yaml
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from pydantic import BaseModel, Field

DEFAULT_MODEL = "gpt-oss:20b"

SUMMARY_PROMPT = """
You are a concise description generator.
Given an input text extracted from a file, generate a summary in Japanese of exactly 100 characters that clearly explains the file's content and purpose.
Output only the summary text, without any labels, extra words, or formatting.
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
	llm = OllamaLLM(
		model=DEFAULT_MODEL, 
		base_url="http://localhost:11434", 
		temperature=0,
		num_ctx=8192	# 8192で14GBくらいになる
	)
	return llm.invoke([
		("system", SUMMARY_PROMPT),
		("human", text)
	])
	
def labeling(text):
	tagging_prompt = ChatPromptTemplate.from_template(LABELING_PROMPT)
	llm = OllamaLLM(model=DEFAULT_MODEL, base_url="http://localhost:11434")
	prompt = tagging_prompt.format(input=text, labels=", ".join(loadLabels()))
	return llm.invoke(prompt)

def loadLabels():
	try:
		with open("/var/www/html/OllamaFileSearch/.config/labelList.yaml", "r", encoding="utf-8") as f:
			labels = yaml.safe_load(f)
			if isinstance(labels, dict):
				labels = list(labels.values())
			return labels
	except FileNotFoundError:
		return ["未分類"]

	
