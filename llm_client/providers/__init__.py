"""Implementaciones de cada proveedor.

OpenAI, Anthropic, Gemini y Hugging Face heredan de BaseLLMClient.
Hugging Face es el extra: no está en el notebook del curso.
"""

from llm_client.providers.anthropic_client import AnthropicClient
from llm_client.providers.gemini_client import GeminiClient
from llm_client.providers.huggingface_client import HuggingFaceClient
from llm_client.providers.openai_client import OpenAIClient

__all__ = ["AnthropicClient", "GeminiClient", "HuggingFaceClient", "OpenAIClient"]
