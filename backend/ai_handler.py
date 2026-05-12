def analyze_font_style(image_base64: str):
    # TODO: 未來改成 Gemini / OpenAI 回傳結果
    return {
        "style": ["round", "casual"],
        "stroke": ["medium"],
        "spacing": ["loose"],
        "mood": ["friendly"]
    }


def generate_feedback(user_image: str, reference_text: str, score: int):
    # TODO: 未來改成 Gemini / OpenAI 產生建議
    return "你的字體整體結構不錯，但右側稍微偏擠。"