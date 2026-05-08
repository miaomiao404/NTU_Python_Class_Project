"""
給 Molly 的串接範例
把這段加進你的 backend/main.py
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
import font_library.scoring as scoring

app = FastAPI()


# 你原本的路由保留不動
@app.get("/")
def home():
    return {"message": "Font Mimic Backend is running"}


# 新增：產生參考圖，回傳 PNG 圖片
# 用法：GET /render?char=永&font_filename=MaShanZheng-Regular.ttf
@app.get("/render")
def render(char: str, font_filename: str):
    img_bytes = font_lib.render_reference_bytes(char, font_filename)
    return Response(content=img_bytes, media_type="image/png")


# 新增：評分，回傳分數 + AI 評語
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
    #   "ai_feedback": "..."   # 有設 GEMINI_API_KEY 才會有
    # }
    return result
