"""
Model Provider v6 — Obsługa wielu LLM
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

try:
    from langchain_xai import ChatXAI
except ImportError:
    ChatXAI = None


def get_model(provider: str = "nvidia", model_name: str = None, temperature: float = 0.0):
    provider = provider.lower()
    
    # NVIDIA API Keys Router
    keys = {
        "meta/llama-3.3-70b-instruct": "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",
        "deepseek-ai/deepseek-v4-pro": "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",
        "nvidia/nemotron-3-ultra-550b-a55b": "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"
    }
    
    # Default fallback key if a different model is passed
    api_key = keys.get(model_name, keys["meta/llama-3.3-70b-instruct"])
    # Default fallback model
    actual_model_name = model_name or "meta/llama-3.3-70b-instruct"

    if provider == "hermes" or provider == "nvidia" or provider == "openai":
        # Bezpiecznik dla błędnych nazw na serwerze Nvidii
        if "deepseek-v4-pro" in actual_model_name:
            actual_model_name = "meta/llama-3.3-70b-instruct"
        if "nemotron-3-ultra" in actual_model_name:
            actual_model_name = "meta/llama-3.3-70b-instruct"
            
        return ChatOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            model=actual_model_name,
            temperature=temperature,
            timeout=30,
            max_retries=1
        )
    elif provider == "anthropic":
        return ChatAnthropic(model=model_name or "claude-3-5-sonnet-20241022", temperature=temperature)
    elif provider in ["grok", "xai"]:
        if ChatXAI is None:
            raise ImportError("Zainstaluj: pip install langchain-xai")
        return ChatXAI(model=model_name or "grok-2-latest", temperature=temperature)
    else:
        return ChatOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=keys["meta/llama-3.3-70b-instruct"],
            model="meta/llama-3.3-70b-instruct",
            temperature=temperature
        )