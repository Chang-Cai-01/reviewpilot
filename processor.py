from concurrent.futures import ThreadPoolExecutor, as_completed
from llm_client import analyze_sentiment, generate_reply


def process_single(review: str, brand: str, tone: str, model: str) -> dict:
    result = analyze_sentiment(review, model=model)
    reply = generate_reply(
        review=review,
        sentiment=result.get("sentiment", "neutral"),
        pain_points=result.get("pain_points", []),
        brand=brand,
        tone=tone,
        model=model,
    )
    return {
        "review": review,
        "sentiment": result.get("sentiment", "neutral"),
        "confidence": result.get("confidence", 0),
        "pain_points": "、".join(result.get("pain_points", [])),
        "keywords": "、".join(result.get("keywords", [])),
        "summary": result.get("summary", ""),
        "reply": reply,
    }


def process_batch(reviews, brand, tone, model, progress_callback=None, max_workers=5):
    results = [None] * len(reviews)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single, r, brand, tone, model): i
            for i, r in enumerate(reviews)
        }
        done = 0
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                results[idx] = {
                    "review": reviews[idx],
                    "sentiment": "error",
                    "confidence": 0,
                    "pain_points": "",
                    "keywords": "",
                    "summary": f"处理失败：{e}",
                    "reply": "",
                }
            done += 1
            if progress_callback:
                progress_callback(done, len(reviews))
    return results