"""
Model Provider v6 — Obsługa wielu LLM
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

try:
    from langchain_xai import ChatXAI
except ImportError:
    ChatXAI = None

try:
    from headroom import compress
    HEADROOM_AVAILABLE = True
except ImportError:
    HEADROOM_AVAILABLE = False

class CompressedChatOpenAI(ChatOpenAI):
    def invoke(self, input, config=None, **kwargs):
        if HEADROOM_AVAILABLE and isinstance(input, list):
            try:
                input = compress(input)
            except Exception as e:
                print(f"[Headroom] Kompresja nie powiodła się: {e}")
        return super().invoke(input, config=config, **kwargs)


def get_model(provider: str = "litellm", model_name: str = None, temperature: float = 0.0):
    # LiteLLM jako główny router, z fallbackiem na alias 'os-core-smart'
    actual_model_name = model_name or "os-core-smart"
    
    return CompressedChatOpenAI(
        base_url="http://host.docker.internal:4000/v1",
        api_key="litellm-dummy-key",
        model=actual_model_name,
        temperature=temperature,
        timeout=60,
        max_retries=2
    )