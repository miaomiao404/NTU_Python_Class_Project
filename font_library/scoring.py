"""
評分系統模組
輸入：使用者手寫圖 + 參照字圖
輸出：相似度分數（0-100）＋ AI 文字講解
"""

import io
import os
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
_DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")


# ── 內部工具 ────────────────────────────────────────────────────────

def _to_gray_array(img: Image.Image, size: tuple[int, int] = (256, 256)) -> np.ndarray:
    return np.array(img.convert("L").resize(size))


def _binarize(arr: np.ndarray) -> np.ndarray:
    """Otsu 自動二值化，回傳筆畫為白(255)、背景為黑(0)的影像"""
    _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


# ── 幾何評分 ─────────────────────────────────────────────────────────

def geometric_score(
    user_img: Image.Image,
    reference_img: Image.Image,
) -> dict:
    """
    計算使用者手寫與參照字的幾何相似度。

    回傳:
        {
            "stroke_accuracy": float,   # 筆畫重疊率 0-100
            "structure":       float,   # 輪廓結構相似度 0-100
            "overall":         float,   # 加權總分 0-100
        }
    """
    size = (256, 256)
    user_bin = _binarize(_to_gray_array(user_img, size))
    ref_bin  = _binarize(_to_gray_array(reference_img, size))

    # 1. Jaccard 相似度（筆畫像素重疊率）
    intersection = np.logical_and(user_bin > 0, ref_bin > 0).sum()
    union        = np.logical_or(user_bin > 0, ref_bin > 0).sum()
    jaccard = float(intersection) / float(union) if union > 0 else 0.0

    # 2. Hu Moments 輪廓相似度
    user_hu = _safe_hu_moments(user_bin)
    ref_hu  = _safe_hu_moments(ref_bin)
    dist    = np.linalg.norm(user_hu - ref_hu)
    moment_score = max(0.0, 1.0 - dist / 50.0)

    # 3. 加權總分
    overall = jaccard * 0.5 + moment_score * 0.5

    return {
        "stroke_accuracy": round(jaccard * 100, 1),
        "structure":       round(moment_score * 100, 1),
        "overall":         round(overall * 100, 1),
    }


def _safe_hu_moments(binary: np.ndarray) -> np.ndarray:
    moments = cv2.moments(binary)
    hu = cv2.HuMoments(moments).flatten()
    # log 壓縮，避免數值差距過大
    return -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)


# ── AI 文字講解 ──────────────────────────────────────────────────────

def ai_feedback(
    user_img: Image.Image,
    reference_img: Image.Image,
    api_key: str,
) -> str:
    """
    呼叫 Gemini API，以中文說明使用者手寫的優缺點與改進建議。

    Args:
        user_img:      使用者上傳的手寫圖（PIL Image）
        reference_img: 參照字圖（PIL Image）
        api_key:       Google Gemini API Key

    回傳:
        str — 繁體中文評語
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "請先安裝新版套件：pip install google-genai"

    client = genai.Client(api_key=api_key)

    def to_png_bytes(img: Image.Image) -> bytes:
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()

    prompt = (
        "你是一位專業的中文書法老師。\n"
        "我會提供兩張圖片：\n"
        "  第一張：【參照字】（目標字體風格）\n"
        "  第二張：【學生作品】（使用者的手寫）\n\n"
        "請用繁體中文，條列式給出以下三點評語：\n"
        "1. ✅ 優點：哪些筆畫或結構寫得好\n"
        "2. ⚠️  需改進：具體指出哪些筆畫、比例或結構需要修正\n"
        "3. 💡 建議：一句具體的練習方向\n\n"
        "語氣親切鼓勵，每點不超過兩句話。"
    )

    ref_bytes  = to_png_bytes(reference_img)
    user_bytes = to_png_bytes(user_img)

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=ref_bytes,  mime_type="image/png"),
            types.Part.from_bytes(data=user_bytes, mime_type="image/png"),
        ],
    )
    return response.text


# ── 主要對外介面 ──────────────────────────────────────────────────────

def score(
    user_img: Image.Image,
    reference_img: Image.Image,
    api_key: str = None,
) -> dict:
    api_key = api_key or _DEFAULT_API_KEY
    """
    完整評分流程。

    Args:
        user_img:      使用者上傳的手寫圖
        reference_img: 由 font_library.render_reference() 產生的參照字圖
        api_key:       Gemini API Key（可選；不填則跳過 AI 評語）

    回傳範例:
        {
            "stroke_accuracy": 72.5,   # 筆畫重疊率
            "structure":       68.0,   # 輪廓結構相似度
            "overall":         70.2,   # 加權總分
            "ai_feedback":     "...",  # AI 文字評語（有 api_key 才會有）
        }
    """
    result = geometric_score(user_img, reference_img)

    if api_key:
        try:
            result["ai_feedback"] = ai_feedback(user_img, reference_img, api_key)
        except Exception as e:
            result["ai_feedback"] = f"AI 評語暫時無法使用：{e}"
    else:
        result["ai_feedback"] = None

    return result


# ── 快速測試 ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    from font_library import render_reference, list_fonts

    fonts = list_fonts()
    if not fonts:
        print("請先執行 download_fonts.py 下載字體")
    else:
        test_font = fonts[0]["filename"]
        ref_img = render_reference("永", test_font)

        # 模擬使用者手寫：把參照字加一點雜訊
        import random
        user_img = ref_img.copy()
        pixels = user_img.load()
        w, h = user_img.size
        for _ in range(3000):
            x, y = random.randint(0, w - 1), random.randint(0, h - 1)
            pixels[x, y] = random.randint(0, 255)

        result = score(user_img, ref_img)
        print(f"字體: {test_font}")
        print(f"筆畫準確度: {result['stroke_accuracy']} / 100")
        print(f"結構相似度: {result['structure']} / 100")
        print(f"總分:       {result['overall']} / 100")
        if result["ai_feedback"]:
            print(f"\nAI 評語:\n{result['ai_feedback']}")
        else:
            print("（未提供 API Key，略過 AI 評語）")
