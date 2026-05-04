from fastapi import FastAPI
from matcher import match_font

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Font Mimic Backend is running"}


@app.get("/analyze")
def analyze():
    ai_result = {
        "style": ["round", "casual"],
        "stroke": ["medium"],
        "spacing": ["loose"],
        "mood": ["friendly"]
    }

    matched_font = match_font(ai_result)

    return {
        "ai_tags": ai_result,
        "matched_font": matched_font
    }