from langchain_ollama.llms import OllamaLLM

def summarize4description(text):
	llm = OllamaLLM(model="gpt-oss:20b")

	return llm.invoke([
		("system", """
You are a concise description generator. 
Given an input text extracted from a file, generate a 100-character summary that clearly describes the content and purpose of the file. 
The output must be exactly the description text only, without any extra words, labels, or formatting. 
"""),
		("human", text)
	])
	
def labeling(text):
	return "test"
