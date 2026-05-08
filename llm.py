import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:32b")


def call_llm(prompt: str, temperature: float = 0.1) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 8192
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return "错误：无法连接 Ollama。请确认 Ollama 已经启动。"

    except requests.exceptions.Timeout:
        return "错误：模型响应超时。可以换成 qwen2.5-coder:14b。"

    except Exception as e:
        return f"错误：{str(e)}"