"""
給 Molly 的串接範例
把這段加進你的 backend/main.py

完整流程：
  1. POST /match-font  → 使用者上傳字體圖片，分析後回傳最像的字體檔名
  2. GET  /render      → 用字體檔名產生參考圖，回傳給前端
  3. POST /score       → 使用者手寫完，比對手寫圖和參考圖，回傳分數
"""

import sys
import os

# 讓 Python 找得到 font_library 資料夾
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from PIL import Image
import io

import font_library.font_library as font_lib
import font_library.analyzer as analyzer
import font_library.scoring as scoring

app = FastAPI()


# 你原本的路由保留不動
@app.get("/")
def home():
    return {"message": "Font Mimic Backend is running"}


# 步驟一：使用者上傳字體圖片，分析後回傳最像的字體
# 用法：POST /match-font，傳一個圖檔（font_image）
@app.post("/match-font")
async def match_font(font_image: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await font_image.read()))

    scores = analyzer.analyze_image(img)   # 分析圖片，得到五項分數
    result = analyzer.match_font(scores)   # 找出最像的字體

    return {
        "font_name":     result["font_name"],
        "filename":      result["filename"],   # 這個存起來，步驟二要用
        "image_scores":  scores,               # 圖片分析出來的分數
        "font_scores":   result["scores"],     # 配對字體的分數
        "distance":      result["distance"],
    }


# 步驟二：用字體檔名產生參考圖，回傳 PNG 給前端顯示
# 用法：GET /render?char=永&font_filename=MaShanZheng-Regular.ttf
@app.get("/render")
def render(char: str, font_filename: str):
    img_bytes = font_lib.render_reference_bytes(char, font_filename)
    return Response(content=img_bytes, media_type="image/png")


# 步驟三：使用者手寫完，比對手寫圖和參考圖，回傳分數
# 用法：POST /score，傳兩個圖檔（user_image, reference_image）
@app.post("/score")
async def score_handwriting(
    user_image: UploadFile = File(...),
    reference_image: UploadFile = File(...),
):
    user_img = Image.open(io.BytesIO(await user_image.read()))
    ref_img  = Image.open(io.BytesIO(await reference_image.read()))

    result = scoring.score(user_img, ref_img)

    # result 長這樣：
    # {
    #   "stroke_accuracy": 72.5,
    #   "structure": 68.0,
    #   "overall": 70.2,
    #   "ai_feedback": "..."
    # }
    return result
