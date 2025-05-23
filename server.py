from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
from collections import Counter

app = FastAPI()

# ===== MCP Request and Response =====

class MCPRequest(BaseModel):
    tool: str
    prompt: str
    context: str

class MCPResponse(BaseModel):
    result: str

# ===== Tool 1: Naive Summarizer =====

def summarize(context: str, prompt: str) -> str:
    sentences = re.split(r'(?<=[.!?]) +', context)
    top_sentences = sentences[:3]  # naive top 3 sentences
    return " ".join(top_sentences)

# ===== Tool 2: Basic Grammar Checker =====

def grammar_check(context: str, prompt: str) -> str:
    text = context
    corrections = {
        "i ": "I ",
        " i ": " I ",
        "dont": "don't",
        "cant": "can't",
        "wont": "won't",
        "im ": "I'm ",
        " its ": " it's ",
        " didnt ": " didn't ",
    }
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    return text

# ===== Tool 3: Keyword Extractor =====

def extract_keywords(context: str, prompt: str) -> str:
    words = re.findall(r'\b\w+\b', context.lower())
    stopwords = set(["the", "is", "and", "in", "to", "of", "a", "that", "it", "for", "on", "with", "as", "are", "was"])
    filtered = [w for w in words if w not in stopwords]
    top_keywords = Counter(filtered).most_common(5)
    return ", ".join([kw for kw, count in top_keywords])

# ===== Router =====

@app.post("/mcp")
async def mcp_tool(request: MCPRequest):
    tool = request.tool.lower()
    if tool == "summarize":
        result = summarize(request.context, request.prompt)
    elif tool == "grammar_check":
        result = grammar_check(request.context, request.prompt)
    elif tool == "keywords":
        result = extract_keywords(request.context, request.prompt)
    else:
        result = f"Unknown tool: {request.tool}"
    return MCPResponse(result=result)

