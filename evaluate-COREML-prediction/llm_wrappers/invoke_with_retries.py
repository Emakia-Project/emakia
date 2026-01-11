def call_openai(texts):
    predictions = []
    for text in texts:
        try:
            response = invoke_with_retries(content_chain, text).lower()
            # Interpret response into binary prediction
            if "positive" in response or "neutral" in response:
                predictions.append(1)
            elif "negative" in response or any(term in response for term in [
                "harmful", "sexual", "slur", "violence", "hate", "discriminatory", "abuse", "harassment"
            ]):
                predictions.append(0)
            else:
                predictions.append(0)  # Default to toxic
        except Exception as e:
            print(f"OpenAI failed on: {text[:50]}... → {e}")
            predictions.append(0)  # Fail-safe
        time.sleep(1.2)  # Optional: throttle between successful requests
    return predictions
