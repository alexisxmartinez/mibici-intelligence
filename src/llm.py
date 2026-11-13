"""One chat function, three backends, tried in order. The app must work with none of them.

1. Ollama on Koatl (or any Ollama): OLLAMA_URL, OLLAMA_MODEL      local, free, private
2. Gemini via AI Studio:            GEMINI_API_KEY, GEMINI_MODELS  comma separated, tried in order
3. None:                            chat() returns None and the caller shows the deterministic answer

Standard library only, so a broken pip install cannot take the copilot down.
"""
from __future__ import annotations
import json, os, urllib.request

TIMEOUT = int(os.getenv("LLM_TIMEOUT", "40"))


def _post(url, body, headers=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def _ollama(messages, tools):
    url, model = os.getenv("OLLAMA_URL"), os.getenv("OLLAMA_MODEL", "qwen3:4b")
    if not url:
        return None
    body = {"model": model, "messages": messages, "stream": False, "think": False, "options": {"temperature": 0.2}}
    if tools:
        body["tools"] = tools
    msg = _post(url.rstrip("/") + "/api/chat", body).get("message", {})
    calls = [{"name": c["function"]["name"], "args": c["function"].get("arguments") or {}} for c in msg.get("tool_calls") or []]
    return {"text": msg.get("content") or "", "tool_calls": calls, "backend": "ollama:" + model}


def _gemini(messages, tools):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None
    system = " ".join(m["content"] for m in messages if m["role"] == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages if m["role"] in ("user", "assistant", "tool")]
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = [{"functionDeclarations": [{"name": t["function"]["name"], "description": t["function"].get("description", ""), "parameters": t["function"].get("parameters", {"type": "object", "properties": {}})} for t in tools]}]
    last = None
    for model in os.getenv("GEMINI_MODELS", "gemini-3.5-flash,gemini-3.5-flash-lite").split(","):
        try:
            d = _post("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model.strip(), body, {"x-goog-api-key": key})
            parts = d["candidates"][0]["content"].get("parts", [])
            calls = [{"name": p["functionCall"]["name"], "args": p["functionCall"].get("args") or {}} for p in parts if "functionCall" in p]
            return {"text": "".join(p.get("text", "") for p in parts), "tool_calls": calls, "backend": "gemini:" + model.strip()}
        except Exception as e:  # 503 and 429 are common on the free tier: try the next model
            last = e
    raise last


def chat(messages, tools=None):
    """messages: [{"role": "system"|"user"|"assistant"|"tool", "content": str}]
    tools: OpenAI-style function specs. Returns {"text", "tool_calls": [{"name", "args"}], "backend"} or None."""
    order = [b.strip() for b in os.getenv("LLM_ORDER", "ollama,gemini").split(",")]
    for name in order:
        fn = {"ollama": _ollama, "gemini": _gemini}.get(name)
        if not fn:
            continue
        try:
            out = fn(messages, tools)
            if out:
                return out
        except Exception:
            continue
    return None


def status() -> str:
    """One line for the sidebar: which backend answers right now."""
    r = chat([{"role": "user", "content": "Responde solo: OK"}])
    return r["backend"] if r else "sin modelo (modo determinista)"
