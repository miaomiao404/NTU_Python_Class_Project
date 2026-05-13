"""
評分系統模組
輸入：使用者手寫圖 + 參照字圖 + 目標字體五項分數
輸出：五項維度分數、總分、Gemini 評語、雷達圖
"""

import io
import os
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
_DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")


# ── 內部工具 ─────────────────────────────────────────────────────────

def _to_gray_binary(img: Image.Image, size=(256, 256)) -> np.ndarray:
    arr = np.array(img.convert("L").resize(size))
    _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary

def _ink_bbox(binary: np.ndarray):
    rows = np.any(binary > 0, axis=1)
    cols = np.any(binary > 0, axis=0)
    if not rows.any() or not cols.any():
        return None
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]
    return int(x1), int(y1), int(x2), int(y2)


# ── OpenCV 五項測量 ───────────────────────────────────────────────────

def _measure_all(binary: np.ndarray) -> dict:
    bbox = _ink_bbox(binary)
    if bbox is None:
        return {"weight": 0.2, "spacing": 0.75, "aspect": 0.93, "slant": 70.0, "roundness": 0.25}

    x1, y1, x2, y2 = bbox
    region = binary[y1:y2, x1:x2]
    w, h = x2 - x1, y2 - y1
    total = region.size

    # 粗細
    weight = float(np.sum(region > 0)) / total

    # 間距
    spacing = float(np.sum(region == 0)) / total

    # 字寬高比
    aspect = w / h if h > 0 else 1.0

    # 斜體（PCA 主軸角度）
    coords = np.column_stack(np.where(binary > 0)).astype(np.float32)
    if len(coords) >= 20:
        mean = coords.mean(axis=0)
        _, _, vt = np.linalg.svd(coords - mean, full_matrices=False)
        angle = np.degrees(np.arctan2(vt[0][1], vt[0][0]))
        slant = float(abs(90 - abs(angle)))
    else:
        slant = 70.0

    # 圓潤度
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circ_scores = [
        4 * np.pi * cv2.contourArea(c) / (cv2.arcLength(c, True) ** 2)
        for c in contours
        if cv2.contourArea(c) > 50 and cv2.arcLength(c, True) > 0
    ]
    roundness = float(np.mean(circ_scores)) if circ_scores else 0.25

    return {"weight": weight, "spacing": spacing, "aspect": aspect,
            "slant": slant, "roundness": roundness}


def _to_score(raw: dict) -> dict:
    def sw(v):
        if v < 0.18: return 1
        if v < 0.25: return 2
        if v < 0.32: return 3
        if v < 0.43: return 4
        return 5

    def ss(v):
        if v < 0.62:  return 1
        if v < 0.70:  return 2
        if v < 0.755: return 3
        if v < 0.82:  return 4
        return 5

    def sa(v):
        if v < 0.80:  return 1
        if v < 0.93:  return 2
        if v < 0.950: return 3
        if v < 0.968: return 4
        return 5

    def sl(v):
        if v > 75: return 1
        if v > 65: return 2
        if v > 57: return 3
        if v > 50: return 4
        return 5

    def sr(v):
        if v < 0.23: return 1
        if v < 0.27: return 2
        if v < 0.32: return 3
        if v < 0.37: return 4
        return 5

    return {
        "weight":    sw(raw["weight"]),
        "spacing":   ss(raw["spacing"]),
        "aspect":    sa(raw["aspect"]),
        "slant":     sl(raw["slant"]),
        "roundness": sr(raw["roundness"]),
    }


# ── Gemini 評語 ───────────────────────────────────────────────────────

def _gemini_feedback(user_img: Image.Image, reference_img: Image.Image,
                     user_scores: dict, target_scores: dict, api_key: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "請先安裝：pip install google-genai"

    client = genai.Client(api_key=api_key)

    def to_png(img):
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()

    dim_names = {"weight": "粗細", "spacing": "間距",
                 "aspect": "字寬高比", "slant": "斜體", "roundness": "圓潤度"}

    score_summary = "\n".join(
        f"  {dim_names[k]}：你的分數 {user_scores[k]} / 目標 {target_scores[k]}"
        for k in dim_names
    )

    prompt = (
        "你是一位親切的中文書法老師。\n"
        "我會給你兩張圖片和一份量化分析結果：\n"
        "  第一張：【參照字】（目標風格）\n"
        "  第二張：【學生作品】（使用者手寫）\n\n"
        f"量化分析（各項 1-5 分）：\n{score_summary}\n\n"
        "請用繁體中文，條列式給出：\n"
        "1. ✅ 優點：哪些筆畫或結構寫得好\n"
        "2. ⚠️  需改進：具體指出哪些分數差距大的地方\n"
        "3. 💡 建議：一句具體的練習方向\n\n"
        "語氣親切鼓勵，每點不超過兩句話。"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=to_png(reference_img), mime_type="image/png"),
            types.Part.from_bytes(data=to_png(user_img),      mime_type="image/png"),
        ],
    )
    return response.text


# ── 雷達圖 ────────────────────────────────────────────────────────────

def generate_radar_chart(user_scores: dict, target_scores: dict) -> bytes:
    """
    產生五角雷達圖，回傳 PNG bytes。
    藍色 = 目標字體分數，橘色 = 使用者分數。
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams["font.family"] = ["Microsoft JhengHei", "Arial Unicode MS",
                                          "Noto Sans CJK TC", "DejaVu Sans"]

    labels = ["粗細", "間距", "字寬高比", "斜體", "圓潤度"]
    keys   = ["weight", "spacing", "aspect", "slant", "roundness"]
    N = len(labels)

    target_vals = [target_scores.get(k, 3) for k in keys]
    user_vals   = [user_scores.get(k, 3)   for k in keys]

    # 閉合多邊形
    target_vals += target_vals[:1]
    user_vals   += user_vals[:1]

    angles = [n / N * 2 * np.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], labels, fontsize=12)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8)

    ax.plot(angles, target_vals, "o-", linewidth=2, color="#4A90D9", label="目標")
    ax.fill(angles, target_vals, alpha=0.15, color="#4A90D9")

    ax.plot(angles, user_vals, "o-", linewidth=2, color="#E87040", label="你的作品")
    ax.fill(angles, user_vals, alpha=0.15, color="#E87040")

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
    plt.title("五維度比對", fontsize=13, pad=15)

    buf = io.BytesIO()
    plt.savefig(buf, format="PNG", bbox_inches="tight", dpi=120)
    plt.close(fig)
    return buf.getvalue()


# ── 主要對外介面 ──────────────────────────────────────────────────────

def score(
    user_img: Image.Image,
    reference_img: Image.Image,
    target_scores: dict,
    api_key: str = None,
    include_chart: bool = True,
) -> dict:
    """
    完整評分流程。

    Args:
        user_img:      使用者手寫圖（PIL Image）
        reference_img: 參照字圖（PIL Image）
        target_scores: 目標字體五項分數（來自 font_scores.json）
        api_key:       Gemini API Key（可選）
        include_chart: 是否產生雷達圖（預設 True）

    回傳:
        {
            "user_scores":    dict,   # 使用者五項分數
            "target_scores":  dict,   # 目標字體五項分數
            "distance":       int,    # 曼哈頓距離（越小越像）
            "overall":        float,  # 0-100 總分
            "ai_feedback":    str,    # Gemini 評語
            "chart_png":      bytes,  # 雷達圖 PNG（None 若 include_chart=False）
        }
    """
    api_key = api_key or _DEFAULT_API_KEY

    user_binary = _to_gray_binary(user_img)
    user_scores = _to_score(_measure_all(user_binary))

    keys = ["weight", "spacing", "aspect", "slant", "roundness"]
    distance = sum(abs(user_scores[k] - target_scores.get(k, 3)) for k in keys)
    overall  = round(max(0.0, 100 - distance * 5), 1)

    result = {
        "user_scores":   user_scores,
        "target_scores": target_scores,
        "distance":      distance,
        "overall":       overall,
        "ai_feedback":   None,
        "chart_png":     None,
    }

    if api_key:
        try:
            result["ai_feedback"] = _gemini_feedback(
                user_img, reference_img, user_scores, target_scores, api_key
            )
        except Exception as e:
            result["ai_feedback"] = f"AI 評語暫時無法使用：{e}"

    if include_chart:
        try:
            result["chart_png"] = generate_radar_chart(user_scores, target_scores)
        except Exception as e:
            result["chart_png"] = None

    return result


# ── 快速測試 ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from font_library import render_reference, list_fonts
    import json, random

    fonts = list_fonts()
    if not fonts:
        print("請先執行 download_fonts.py")
    else:
        test_font = fonts[0]["filename"]
        ref_img = render_reference("永", test_font)

        # 模擬手寫（加雜訊）
        user_img = ref_img.copy()
        pixels = user_img.load()
        w, h = user_img.size
        for _ in range(3000):
            x, y = random.randint(0, w-1), random.randint(0, h-1)
            pixels[x, y] = random.randint(0, 255)

        # 讀目標分數
        scores_path = os.path.join(os.path.dirname(__file__), "font_scores.json")
        with open(scores_path, encoding="utf-8") as f:
            registry = json.load(f)
        target = next((r["scores"] for r in registry if r["filename"] == test_font), None)

        if target:
            result = score(user_img, ref_img, target)
            print(f"字體：{test_font}")
            print(f"使用者分數：{result['user_scores']}")
            print(f"目標分數：  {result['target_scores']}")
            print(f"距離：{result['distance']}，總分：{result['overall']}/100")
            if result["chart_png"]:
                with open("test_chart.png", "wb") as f:
                    f.write(result["chart_png"])
                print("雷達圖已儲存：test_chart.png")
