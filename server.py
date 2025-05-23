from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import re
from collections import Counter

app = FastAPI()

# ===== MCP Request and Response =====

class MCPRequest(BaseModel):
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

import language_tool_python

tool = language_tool_python.LanguageTool('en-US')

def grammar_check(context, prompt):
    matches = tool.check(context)
    corrected = language_tool_python.utils.correct(context, matches)
    return corrected

# ===== Tool 3: Keyword Extractor =====

def extract_keywords(context: str, prompt: str) -> str:
    words = re.findall(r'\b\w+\b', context.lower())
    stopwords = set(["the", "is", "and", "in", "to", "of", "a", "that", "it", "for", "on", "with", "as", "are", "was"])
    filtered = [w for w in words if w not in stopwords]
    top_keywords = Counter(filtered).most_common(5)
    return ", ".join([kw for kw, count in top_keywords])


#======
def route_tool(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if "summarize" in prompt_lower or "summary" in prompt_lower:
        return "summarize"
    elif "grammar" in prompt_lower or "correct" in prompt_lower or "fix" in prompt_lower:
        return "grammar_check"
    elif "keywords" in prompt_lower or "important words" in prompt_lower:
        return "keywords"
    else:
        return "unknown"

# ===== Router =====

@app.post("/mcp")
async def mcp_tool(request: MCPRequest):
    tool = route_tool(request.prompt)
    
    if tool == "summarize":
        result = summarize(request.context, request.prompt)
    elif tool == "grammar_check":
        result = grammar_check(request.context, request.prompt)
    elif tool == "keywords":
        result = extract_keywords(request.context, request.prompt)
    else:
        result = f"Unknown or unhandled tool routed from prompt."
    
    return MCPResponse(result=result)

