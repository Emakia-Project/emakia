import time
import openai

def safe_call(fn, *args, retries=3, **kwargs):
    for i in range(retries):
        try:
            return fn(*args, **kwargs)
        except openai.RateLimitError as e:
            print(f"⚠️ Retry {i+1}/{retries} after rate limit")
            time.sleep(20)
    return {"result": "⚠️ Unknown"}
