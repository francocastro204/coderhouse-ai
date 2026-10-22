"""Paquete llm_client: el cliente async unificado.

Desde acá se importan las piezas públicas, sin conocer la ruta interna
de cada archivo:

    from unidad_1.pre_entrega.llm_client import AsyncLLMManager, ChatMessage, LLMConfig, Provider
"""

from unidad_1.pre_entrega.llm_client.manager import AsyncLLMManager
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, LLMConfig, ModelResponse, Provider

__all__ = [
    "AsyncLLMManager",
    "ChatMessage",
    "LLMConfig",
    "ModelResponse",
    "Provider",
]
