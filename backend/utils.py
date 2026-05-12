# utils.py
# 放共用工具函式，例如 base64 處理、格式檢查等
# utils.py

import base64


def remove_base64_header(base64_str: str):
    """
    移除 data:image/png;base64, 前綴
    """
    if "," in base64_str:
        return base64_str.split(",")[1]
    return base64_str


def is_empty_string(text: str):
    """
    檢查字串是否為空
    """
    return text.strip() == ""


def safe_base64_decode(base64_str: str):
    """
    安全解碼 Base64
    """
    try:
        base64_str = remove_base64_header(base64_str)
        return base64.b64decode(base64_str)
    except Exception:
        return None