# FontMimic-Web 前後端 API 規格與對接指南

本文件定義了 FontMimic 專案中，前端 Web 介面與後端 Python (FastAPI) 之間的溝通合約。請後端開發人員依照此規格實作 API 路由。

## 注意事項

在開始寫路由之前，請務必確認以下三件事，否則前端將完全無法與後端連線：

1. **必須啟用 CORS (跨域資源共用)**
前端通常跑在 `Live Server (Port 5500)`，後端跑在 `FastAPI (Port 8000)`。請務必在 `main.py` 中引入 `CORSMiddleware` 並允許所有來源（或指定前端網址），否則瀏覽器會直接阻擋請求。
2. **所有涉及圖片的 API 都必須是 `POST` 方法**
因為圖片轉換後的 Base64 字串非常長，超過了 `GET` 請求的網址長度限制，因此本專案所有的功能 API 皆採用 `POST` 傳輸 JSON。
3. **注意 Base64 的「前綴字串」**
前端傳過來的 Base64 圖片字串，開頭會帶有 MIME type 宣告，例如：
`data:image/png;base64,iVBORw0KGgo...` 或 `data:image/jpeg;base64,/9j/4AAQSkZ...`
**後端在進行 `base64.b64decode()` 之前，必須先用 Python 把逗號前面的字串（包含逗號）切掉 (split)！**

## 📡 API 路由規格

目前前端總共會呼叫 3 支 API，Base URL 預設為 `http://127.0.0.1:8000`。

### 1. 解析字體風格 API

* **端點**: `/analyze`
* **方法**: `POST`
* **功能**: 接收使用者上傳的圖片，透過 AI 分析出風格標籤，並與本地端 `registry.json` 匹配出最適合的字體。

**前端發送 (Request Body - JSON):**

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgo..." // 使用者上傳的圖片
}

```

**後端回傳 (Response Body - JSON):**

```json
{
  "ai_tags": {
    "style": ["round", "casual"],
    "stroke": ["medium"],
    "mood": ["friendly"]
  },
  "matched_font": {
    "font_name": "粉圓體",
    "file_path": "fonts/jf-openhuninn.ttf",
    "score": 3
  }
}

```

*(備註：前端會將 `ai_tags` 儲存起來，留待下一步生成圖片時使用。)*

---

### 2. 生成參考圖片 API

* **端點**: `/generate`
* **方法**: `POST`
* **功能**: 接收使用者想練習的文字與剛才解析出的風格標籤，後端使用 Pillow + OpenCV 渲染出該風格的文字圖片。

**前端發送 (Request Body - JSON):**

```json
{
  "text": "你好", // 使用者想練習的字
  "tags": { // 這裡會把 /analyze 拿到的 ai_tags 原封不動傳回去
    "style": ["round", "casual"],
    "stroke": ["medium"],
    "mood": ["friendly"]
  }
}

```

**後端回傳 (Response Body - JSON):**

```json
{
  "generated_image_base64": "data:image/png;base64,iVBORw0KGgo..." // OpenCV 處理完的參考圖
}

```

*(備註：後端回傳的 base64 請務必確保帶有 `data:image/png;base64,` 這樣的前綴，前端的 `<img>` 標籤才能直接顯示。)*

---

### 3. 送出實作評分 API

* **端點**: `/score`
* **方法**: `POST`
* **功能**: 接收前端 Canvas 畫布上的手寫圖與目標文字，透過 OpenCV 計算幾何分數，並透過 Gemini AI 產生文字建議。

**前端發送 (Request Body - JSON):**

```json
{
  "user_image": "data:image/png;base64,iVBORw0KGgo...", // 前端 Canvas 輸出的手寫圖片
  "reference_text": "你好" // 讓 AI 知道使用者在寫什麼字
}

```

**後端回傳 (Response Body - JSON):**

```json
{
  "score": 85, // 0~100 的整數分數
  "feedback": "你的「你」字右半邊稍微太擠了，可以嘗試將部首分開一點，讓整體結構更平衡。" // AI 給的中文建議
}

```

---

## 後端實作小提示 (Python 範例)

**處理前端 CORS 的 FastAPI 寫法：**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開發階段允許所有來源，上線時請改為前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

```

**處理 Base64 轉換為 OpenCV 圖片的寫法：**

```python
import base64
import numpy as np
import cv2

def decode_base64_to_cv2(base64_str: str):
    # 切除前綴，只留逗號後面的純 Base64 編碼
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return img_cv2

```