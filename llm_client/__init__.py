"""Paquete llm_client: el cliente async unificado.

Desde acá se importan las piezas públicas, sin conocer la ruta interna
de cada archivo:

    from llm_client import AsyncLLMManager, ChatMessage, LLMConfig, Provider
"""

from llm_client.manager import AsyncLLMManager
from llm_client.schemas import ChatMessage, LLMConfig, ModelResponse, Provider

__all__ = [
    "AsyncLLMManager",
    "ChatMessage",
    "LLMConfig",
    "ModelResponse",
    "Provider",
]
