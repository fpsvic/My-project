"""
Fallback API chain: tries multiple external AI providers in order until one succeeds.
Providers attempted: OpenAI → Anthropic → Groq → Together AI → Ollama (local).
Each is only tried if its API key env var is set (or Ollama if reachable).
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional

_TIMEOUT = 20  # seconds per provider attempt

SYSTEM_PROMPT = (
    "You are ForgeAI, a helpful and knowledgeable AI assistant. "
    "Answer clearly and concisely. Use markdown formatting where appropriate."
)


def _post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode())


def _try_openai(query: str, history: list) -> Optional[str]:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-6:]:
        messages.append({"role": m.get("role", "user"), "content": m.get("text", "")})
    messages.append({"role": "user", "content": query})
    try:
        resp = _post_json(
            "https://api.openai.com/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            {"model": "gpt-4o-mini", "messages": messages, "max_tokens": 1024},
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return None


def _try_anthropic(query: str, history: list) -> Optional[str]:
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    messages = []
    for m in history[-6:]:
        role = "assistant" if m.get("role") == "assistant" else "user"
        messages.append({"role": role, "content": m.get("text", "")})
    messages.append({"role": "user", "content": query})
    try:
        resp = _post_json(
            "https://api.anthropic.com/v1/messages",
            {
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
            {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": messages,
            },
        )
        return resp["content"][0]["text"]
    except Exception:
        return None


def _try_groq(query: str, history: list) -> Optional[str]:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return None
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-6:]:
        messages.append({"role": m.get("role", "user"), "content": m.get("text", "")})
    messages.append({"role": "user", "content": query})
    try:
        resp = _post_json(
            "https://api.groq.com/openai/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            {"model": "llama-3.1-8b-instant", "messages": messages, "max_tokens": 1024},
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return None


def _try_together(query: str, history: list) -> Optional[str]:
    key = os.getenv("TOGETHER_API_KEY", "")
    if not key:
        return None
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-6:]:
        messages.append({"role": m.get("role", "user"), "content": m.get("text", "")})
    messages.append({"role": "user", "content": query})
    try:
        resp = _post_json(
            "https://api.together.xyz/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            {"model": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo", "messages": messages, "max_tokens": 1024},
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return None


def _try_ollama(query: str, history: list) -> Optional[str]:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in history[-6:]:
        messages.append({"role": m.get("role", "user"), "content": m.get("text", "")})
    messages.append({"role": "user", "content": query})
    try:
        resp = _post_json(
            f"{host}/api/chat",
            {"Content-Type": "application/json"},
            {"model": model, "messages": messages, "stream": False},
        )
        return resp["message"]["content"]
    except Exception:
        return None


_PROVIDERS = [
    ("OpenAI GPT-4o-mini", _try_openai),
    ("Anthropic Claude Haiku", _try_anthropic),
    ("Groq Llama-3.1", _try_groq),
    ("Together Llama-3.2", _try_together),
    ("Ollama (local)", _try_ollama),
]


def call_fallback_apis(query: str, history: list) -> Optional[str]:
    """
    Try each provider in order. Return the first successful response, or None
    if all providers fail or none are configured.
    """
    for name, fn in _PROVIDERS:
        result = fn(query, history)
        if result and result.strip():
            return f"*[via {name}]*\n\n{result}"
    return None
