import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_font_style_from_base64(image_base64: str) -> dict:
    """
    接收前端傳來的 base64 圖片，
    丟給 OpenAI Vision 分析，
    回傳符合前端規格的 ai_tags。
    """

    prompt = """
你是一個中文字體風格分析系統。

請分析圖片中的中文字體，只輸出 JSON，不要 Markdown，不要解釋。

JSON 格式必須如下：

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

4. 如果不確定，請使用：
{
  "style": ["sans"],
  "stroke": ["medium"],
  "mood": ["clean"]
}
"""

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

    try:
        tags = json.loads(raw_text)
    except Exception:
        tags = fallback_tags()

    return validate_tags(tags)


def fallback_tags() -> dict:
    return {
        "style": ["sans"],
        "stroke": ["medium"],
        "mood": ["clean"]
    }


def validate_tags(tags: dict) -> dict:
    allowed_style = [
        "sans", "serif", "round", "handwriting",
        "calligraphy", "casual", "formal"
    ]
    allowed_stroke = ["thin", "medium", "bold"]
    allowed_mood = ["friendly", "elegant", "traditional", "clean", "cute"]

    style = tags.get("style", [])
    stroke = tags.get("stroke", [])
    mood = tags.get("mood", [])

    if not isinstance(style, list):
        style = [style]

    if not isinstance(stroke, list):
        stroke = [stroke]

    if not isinstance(mood, list):
        mood = [mood]

    style = [x for x in style if x in allowed_style]
    stroke = [x for x in stroke if x in allowed_stroke]
    mood = [x for x in mood if x in allowed_mood]

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