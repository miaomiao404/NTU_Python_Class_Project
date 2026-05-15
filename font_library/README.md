# Font Library 模組說明
**負責人：陳佳馨**

---

## 我負責的範圍

| 項目 | 說明 |
|---|---|
| 字體庫建立 | 收集 26 套開源中文字體，撰寫自動下載腳本 |
| 字體分析比對 | OpenCV 分析使用者上傳的範本圖片，找出最相近的字體 |
| 評分系統 | OpenCV 比對手寫與目標字體，給出五項分數與總分 |
| AI 評語 | 呼叫 Gemini API，給出繁中書法建議 |
| 雷達圖 | matplotlib 產生五角雷達圖，顯示使用者與目標字體的分數差距 |

---

## 檔案說明

| 檔案 | 功能 |
|---|---|
| `download_fonts.py` | 自動下載 26 套字體到 `fonts/` 資料夾，執行一次即可 |
| `font_library.py` | 管理字體庫、渲染參考圖（`render_reference()`） |
| `analyzer.py` | 分析範本圖片五項分數，比對最像哪套字體（`analyze_image()` + `match_font()`） |
| `scoring.py` | 評分系統，比對手寫圖與目標字體（`score()`） |
| `font_scores.json` | 26 套字體的五項分數資料庫 |
| `registry.json` | 26 套字體的風格標籤（給 Molly 的 matcher 使用） |
| `measure_all_fonts.py` | 量測所有字體的五項原始數值（校正用） |
| `example_for_molly.py` | Molly 串接範例程式碼 |

---

## 五項評分維度

| 維度 | 說明 | 測量方式 |
|---|---|---|
| 粗細（weight） | 筆畫寬度 | 黑色像素佔比 |
| 間距（spacing） | 筆畫疏密 | 空白像素佔比 |
| 字寬高比（aspect） | 字的寬÷高 | 墨水範圍測量 |
| 斜體（slant） | 字的傾斜程度 | PCA 主軸角度 |
| 圓潤度（roundness） | 轉角圓弧程度 | 輪廓圓形度公式 |

每項 1–5 分，閾值依據實際量測 20 套字體後定出。

---

## 完整流程

```
使用者上傳範本圖片
       ↓
analyzer.analyze_image(img)   ← OpenCV 分析五項分數
       ↓
analyzer.match_font(scores)   ← 比對 font_scores.json，找最像字體
       ↓
告訴 Molly（字體檔名 + 目標分數）
       ↓
Molly 呼叫 font_library.render_reference(char, filename) ← 產生參考圖
       ↓
使用者在畫布寫字 / 上傳手寫圖
       ↓
scoring.score(user_img, ref_img, target_scores) ← 評分
       ↓
回傳：五項分數、總分(0-100)、AI評語、雷達圖PNG
```

---

## 比對公式

使用**曼哈頓距離**：

```
距離 = |粗細差| + |間距差| + |字寬高比差| + |斜體差| + |圓潤度差|
總分 = max(0, 100 - 距離 × 5)
```

距離越小 = 越像目標字體。

---

## 環境設定

**安裝套件：**
```bash
pip install -r requirements.txt
```

**設定 Gemini API Key（需要才有 AI 評語）：**
在 `font_library/` 資料夾建立 `.env` 檔案：
```
GEMINI_API_KEY=你的key
```

**下載字體：**
```bash
python download_fonts.py
```

---

## 需要跟組員溝通的事

### 跟 Molly（後端）說
1. 串接範例在 `example_for_molly.py`，後端路由要加三個：
   - `POST /match-font` → 收範本圖，回傳最像字體檔名
   - `GET /render` → 產生參考圖給前端
   - `POST /score` → 回傳分數＋雷達圖
2. 呼叫 `score()` 時要把 `target_scores` 一起傳進來（從 `match_font()` 的回傳值取得）
3. 雷達圖回傳的是 PNG bytes，前端要用 `<img>` 標籤顯示

### 跟秈穎（AI）說
1. AI 評語目前用 Gemini，但台灣帳號免費額度可能是 0，需要確認她的帳號是否有額度
2. Gemini API Key 要放在 `.env` 裡，不能 commit 到 git
3. 如果她的帳號有額度，直接用我的 `scoring.py` 裡的 `_gemini_feedback()` 就好

### 跟苗哲維（前端）說
1. 雷達圖後端會回傳 PNG bytes，前端用 base64 轉換後放進 `<img>` 標籤顯示
2. 評分結果的 JSON 格式：
   ```json
   {
     "user_scores":   {"weight":2, "spacing":4, "aspect":3, "slant":2, "roundness":2},
     "target_scores": {"weight":3, "spacing":3, "aspect":3, "slant":2, "roundness":3},
     "distance": 2,
     "overall": 90.0,
     "ai_feedback": "...",
     "chart_png": "<PNG bytes>"
   }
   ```

---

## 目前狀態

| 功能 | 狀態 |
|---|---|
| 字體下載 | ✅ 完成（20套自動、6套需手動） |
| 字體分析（五項）| ✅ 完成（全 OpenCV） |
| 字體比對 | ✅ 完成 |
| 評分系統 | ✅ 完成（OpenCV + 曼哈頓距離） |
| 雷達圖 | ✅ 完成 |
| AI 評語 | ⚠️ 程式完成，待確認 Gemini 帳號額度 |
| 跟 Molly 串接 | ⏳ 待 Molly 更新後端路由 |
