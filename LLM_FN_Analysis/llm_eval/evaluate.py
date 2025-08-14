from llm_wrappers.openai_wrapper import call_openai
from llm_wrappers.gemini_wrapper import call_gemini
from llm_wrappers.grok_wrapper import call_grok
from llm_wrappers.llama_wrapper import call_llama
from llm_wrappers.deepseek_wrapper import call_deepseek


def evaluate_with_llm(llm_name, rows):
    texts = [row["text"] for row in rows]

    if llm_name == "openai":
        return call_openai(texts)
    elif llm_name == "gemini":
        return call_gemini(texts)
    elif llm_name == "grok":
        return call_grok(texts)
    elif llm_name == "llama":
        return call_llama(texts)
    elif llm_name == "deepseek":
        return call_deepseek(texts)
    else:
        raise ValueError(f"Unknown LLM: {llm_name}")
