import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

#跟 registry.json 不一致
ALLOWED_STYLE = [
    "sans",
    "serif",
    "round",
    "handwriting",
    "calligraphy",
    "casual",
    "formal"
]

ALLOWED_STROKE = [
    "thin",
    "medium",
    "bold"
]

ALLOWED_MOOD = [
    "friendly",
    "elegant",
    "traditional",
    "clean",
    "cute"
]

def analyze_font_style(image_base64: str) -> dict:
    """
    接收前端傳來的 base64 圖片，
    丟給 OpenAI Vision 分析，
    回傳符合前端規格的 ai_tags。
    """

    if client is None:
        return fallback_tags()
    
    prompt = """
你是一個中文字體風格分析系統。

請分析圖片中的中文字體，只輸出 JSON，不要 Markdown，不要解釋。

你只能從指定標籤中選擇。

JSON 格式必須完全符合：

{
  "style": ["round", "casual"],
  "stroke": ["medium"],
  "mood": ["friendly"]
}

規則：
1. style 只能從以下選擇，可複選：
   ["sans", "serif", "round", "handwriting", "calligraphy", "casual", "formal"]

2. stroke 只能從以下選擇，可複選：
   ["thin", "medium", "bold"]

3. mood 只能從以下選擇，可複選：
   ["friendly", "elegant", "traditional", "clean", "cute"]

4. 如果圖片看不清楚，請使用：
{
  "style": ["sans"],
  "stroke": ["medium"],
  "mood": ["clean"]
}

5. 請不要輸出 registry.json 以外的自創標籤。
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": image_base64
                        }
                    ]
                }
            ]
        )

        raw_text = response.output_text.strip()
        tags = parse_json_from_ai(raw_text)
    
        return validate_tags(tags)
    
    except Exception as error:
            print(f"[AI analyze error] {error}")
            tags = fallback_tags()

def parse_json_from_ai(raw_text: str) -> dict:
    """
    將 AI 回傳文字轉成 dict。
    可處理 AI 不小心包上 ```json 的情況。
    """

    if not raw_text:
        return fallback_tags()

    cleaned = raw_text.strip()

    cleaned = cleaned.replace("```json", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return fallback_tags()

    return fallback_tags()

def fallback_tags() -> dict:
    """
    當 AI 沒有正常輸出 JSON 時，使用預設標籤。
    """
    return {
        "style": ["sans"],
        "stroke": ["medium"],
        "mood": ["clean"]
    }


def validate_tags(tags: dict) -> dict:
    """
    檢查 AI 回傳的 tags 是否符合前端規格。
    如果 AI 亂輸出不存在的標籤，就移除或改成預設值。
    """

    if not isinstance(tags, dict):
        return fallback_tags()
    
    style = normalize_to_list(tags.get("style", []))
    stroke = normalize_to_list(tags.get("stroke", []))
    mood = normalize_to_list(tags.get("mood", []))

    style = [item for item in style if item in ALLOWED_STYLE]
    stroke = [item for item in stroke if item in ALLOWED_STROKE]
    mood = [item for item in mood if item in ALLOWED_MOOD]
    
    if len(style) == 0:
        style = ["sans"]

    if len(stroke) == 0:
        stroke = ["medium"]

    if len(mood) == 0:
        mood = ["clean"]

    return {
        "style": style,
        "stroke": stroke,
        "mood": mood
    }

def normalize_to_list(value):
    """
    確保輸入一定會變成 list。
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value]

    return []

def generate_feedback(user_image: str, reference_text: str, score: int) -> str:
    """
    根據使用者手寫圖片、目標文字與 OpenCV 分數，
    使用 AI 產生中文回饋。

    如果沒有 API key 或 AI 失敗，
    會回傳固定版建議。
    """

    if client is None:
        return fallback_feedback(reference_text, score)

    prompt = f"""
你是一位中文字體臨摹老師。

使用者正在練習的文字是：「{reference_text}」
OpenCV 幾何評分是：{score} 分。

請根據這張使用者手寫圖片，給出簡短、具體、友善的中文建議。

請注意：
1. 不要超過 80 字。
2. 請針對筆畫比例、間距、重心、結構提出建議。
3. 不要過度批評。
4. 不要提到你是 AI。
5. 請直接輸出建議文字。
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": user_image
                        }
                    ]
                }
            ]
        )

        feedback = response.output_text.strip()

        if not feedback:
            return fallback_feedback(reference_text, score)

        return feedback

    except Exception as error:
        print(f"[AI feedback error] {error}")
        return fallback_feedback(reference_text, score)
    
def fallback_feedback(reference_text: str, score: int) -> str:
    """
    AI 回饋失敗時使用的預設建議。
    """

    if score >= 85:
        level_comment = "整體結構已經很接近參考字。"
    elif score >= 65:
        level_comment = "整體形狀有抓到，但還可以更穩定。"
    else:
        level_comment = "目前與參考字還有一段差距，可以先放慢速度練習。"

    return (
        f"你這次練習的是「{reference_text}」，目前分數是 {score} 分。"
        f"{level_comment}"
        "建議再注意筆畫間距、左右比例與整體重心。"
    )