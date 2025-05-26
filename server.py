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
from transformers import pipeline

summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(context: str, prompt: str) -> str:
    summary = summarizer_pipeline(context, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# ===== Tool 2: Basic Grammar Checker =====

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

tokenizer = AutoTokenizer.from_pretrained("prithivida/grammar_error_correcter_v1")
model = AutoModelForSeq2SeqLM.from_pretrained("prithivida/grammar_error_correcter_v1")

def grammar_check(context, prompt):
    input_text = f"gec: {context}"
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
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

