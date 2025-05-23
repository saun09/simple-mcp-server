import requests

def call_tool(tool, prompt, context):
    url = "http://localhost:8000/mcp"
    payload = {
        "tool": tool,
        "prompt": prompt,
        "context": context
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"\nTool: {tool}\nResponse:\n{response.json()['result']}\n")
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    context_text = """
    I am writing a report on artificial intelligence. it is a very broad field that includes machine learning, deep learning, and natural language processing.
    i want to explain its applications in healthcare, finance, and education. ai can automate tasks and provide insights from large data sets.
    """
    prompt = "Summarize the above for me."

    call_tool("summarize", prompt, context_text)
    call_tool("grammar_check", prompt, context_text)
    call_tool("keywords", prompt, context_text)
