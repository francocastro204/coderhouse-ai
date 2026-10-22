"""Contrato común de todos los proveedores.

Este archivo define BaseLLMClient, la clase padre. OpenAI, Anthropic y
Gemini heredan de acá e implementan los mismos dos métodos. main.py y el
manager hablan con esta interfaz, no con cada SDK.

Para qué sirve:
- Poder cambiar de proveedor sin cambiar la pregunta.
- Dejar escrito, en un solo lugar, qué debe saber hacer cualquier cliente.

Métodos:
- generate(): espera la respuesta completa y devuelve un ModelResponse.
- generate_stream(): entrega el texto de a pedazos, con yield.

Esta clase no llama a ninguna API.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, ModelResponse


class BaseLLMClient(ABC):
    """Contrato que todo cliente de LLM debe cumplir, sin importar el proveedor."""

    @abstractmethod
    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        """Genera una respuesta completa (modo normal, no streaming)."""
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """Genera la respuesta token a token (modo streaming)."""
        raise NotImplementedError
        yield  # nunca se ejecuta; le indica a Python que este método es un generador
