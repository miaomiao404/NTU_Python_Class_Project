import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(BASE_DIR, "registry.json")

def load_registry():
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

        if not isinstance(registry, list):
            return fallback_registry()

        return registry

    except Exception as error:
        print(f"[matcher] registry.json 載入失敗：{error}")
        return fallback_registry()

def fallback_registry():
    return [
        {
            "font_name": "CuteHandwriting",
            "file_path": "fonts/cute.ttf",
            "tags": {
                "style": ["cute", "round", "casual"],
                "stroke": ["medium"],
                "spacing": ["loose"],
                "mood": ["friendly", "warm"]
            }
        }
    ]

def calculate_score(ai_tags, font_tags):
    score = 0
    categories = ["style", "stroke", "mood"]

    if not isinstance(ai_tags, dict):
        ai_tags = {}

    if not isinstance(font_tags, dict):
        font_tags = {}

    for category in categories:
        ai_values = set(ai_tags.get(category, []))
        font_values = set(font_tags.get(category, []))

        matched_tags = ai_values & font_values
        score += len(matched_tags)

    return score


def match_font(ai_tags):
    registry = load_registry()

    best_font = None
    best_score = -1

    for font in registry:
        font_tags = font.get("tags", {})
        score = calculate_score(ai_tags, font_tags)

        if score > best_score:
            best_score = score
            best_font = font

        if best_font is None:
            best_font = fallback_registry()[0]
            best_score = 0

    return {
        "font_name": best_font["font_name"],
        "file_path": best_font["file_path"],
        "score": best_score
    }