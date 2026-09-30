import os
import json
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from prompts import SENTIMENT_PROMPT, REPLY_PROMPT

load_dotenv()

MODEL_FAST = "claude-3-5-haiku-20241022"
MODEL_STRONG = "claude-3-5-sonnet-20241022"

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("缺少 ANTHROPIC_API_KEY，请检查 .env 文件")
        _client = Anthropic(
            api_key=api_key,
            base_url="https://www.iuseapi.com"   # ← 关键：走中转站
        )
    return _client


def _call_claude(prompt: str, model: str = MODEL_FAST, max_tokens: int = 500) -> str:
    client = get_client()
    last_err = None
    for attempt in range(3):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Claude 调用失败：{last_err}")


def analyze_sentiment(review: str, model: str = MODEL_FAST) -> dict:
    prompt = SENTIMENT_PROMPT.format(review=review)
    raw = _call_claude(prompt, model=model, max_tokens=400)
    return _parse_json(raw)


def generate_reply(review, sentiment, pain_points, brand="我们", tone="亲切", model=MODEL_FAST):
    prompt = REPLY_PROMPT.format(
        brand=brand, tone=tone, review=review,
        sentiment=sentiment,
        pain_points="、".join(pain_points) if pain_points else "无",
    )
    return _call_claude(prompt, model=model, max_tokens=200)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "sentiment": "neutral", "confidence": 0.0,
            "pain_points": [], "keywords": [],
            "summary": "解析失败",
        }