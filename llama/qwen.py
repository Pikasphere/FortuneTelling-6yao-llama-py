# llama/qwen.py
import os
import glob
import threading
from llama_cpp import Llama

_LLM = None
_LOCK = threading.Lock()
_CURRENT_MODEL = None       # 当前已加载的模型路径


# ---------- 模型目录 ----------
_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "gguf",
)


def list_models() -> list:
    """扫描 gguf 目录，返回所有 .gguf 文件名（按名称排序）"""
    if not os.path.isdir(_MODEL_DIR):
        return []
    files = glob.glob(os.path.join(_MODEL_DIR, "*.gguf"))
    return sorted(os.path.basename(f) for f in files)


def get_model_path(filename: str) -> str:
    """把文件名拼成完整路径"""
    return os.path.join(_MODEL_DIR, filename)


SYSTEM_PROMPT = (
    "你是一位严谨的易经解读助手。"
    "你只根据用户提供的卦象、卦辞、爻辞和白话解释来解读，"
    "不要编造没有给出的卦辞或爻辞。"
    "解读要紧密结合用户的具体问题，给出可操作的建议和风险提醒。"
    "如果信息不足，请明确说明，不要强行猜测。"
    "回答控制在 300 字以内。"
)


def load_model(filename: str) -> Llama:
    """
    加载指定模型（按文件名）。
    如果当前已加载同名模型，直接复用；
    否则先释放旧模型，再加载新的。
    """
    global _LLM, _CURRENT_MODEL

    path = get_model_path(filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"模型文件不存在：{path}")

    with _LOCK:
        # 同一个模型，直接复用
        if _LLM is not None and _CURRENT_MODEL == path:
            return _LLM

        # 释放旧模型
        if _LLM is not None:
            try:
                del _LLM
            except Exception:
                pass
            _LLM = None
            _CURRENT_MODEL = None

        # 加载新模型
        _LLM = Llama(
            model_path=path,
            n_ctx=2048,
            n_threads=8,
            n_gpu_layers=0,
            chat_format="qwen",
            verbose=False,
        )
        _CURRENT_MODEL = path

    return _LLM


def is_model_loaded() -> bool:
    return _LLM is not None


def current_model() -> str:
    """返回当前已加载模型的文件名，未加载返回空"""
    if _CURRENT_MODEL is None:
        return ""
    return os.path.basename(_CURRENT_MODEL)


def AI_description(prompt: str) -> str:
    if _LLM is None:
        raise RuntimeError("模型尚未加载")
    resp = _LLM.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=256,
        temperature=0.7,
    )
    return resp["choices"][0]["message"]["content"]