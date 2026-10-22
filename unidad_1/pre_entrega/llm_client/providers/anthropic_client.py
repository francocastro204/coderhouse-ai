"""Cliente de Anthropic (Claude).

Habla con la API de Claude usando AsyncAnthropic. A diferencia de OpenAI,
el system prompt viaja en un parámetro aparte, no dentro de la lista de
mensajes. max_tokens es obligatorio.

Un fallo de key, red o rate limit vuelve como ModelResponse.error.
"""

from typing import AsyncGenerator, List

from anthropic import (
    APIConnectionError as AnthropicConnectionError,
    APIError as AnthropicAPIError,
    AsyncAnthropic,
    RateLimitError as AnthropicRateLimitError,
)

from unidad_1.pre_entrega.llm_client.base import BaseLLMClient
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, ModelResponse, Provider


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self._client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            chat, system = self._separar_system(messages)
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=chat,
                **self._system_kw(system),
            )
            return ModelResponse(
                provider=Provider.ANTHROPIC,
                model=self.model,
                content=response.content[0].text,
            )
        except AnthropicRateLimitError as e:
            return self._error(f"Límite de cuota excedido: {e}")
        except AnthropicConnectionError as e:
            return self._error(f"Error de conexión: {e}")
        except AnthropicAPIError as e:
            return self._error(f"Error de la API de Anthropic: {e}")

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            chat, system = self._separar_system(messages)
            async with self._client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=chat,
                **self._system_kw(system),
            ) as stream:
                async for texto in stream.text_stream:
                    yield texto
        except (AnthropicRateLimitError, AnthropicConnectionError, AnthropicAPIError) as e:
            yield f"\n[Error durante el streaming: {e}]"

    def _separar_system(self, messages: List[ChatMessage]) -> tuple[list[dict], str]:
        """Saca los mensajes system. Anthropic no los acepta dentro de messages."""
        sistema: list[str] = []
        chat: list[dict] = []
        for mensaje in messages:
            if mensaje.role == "system":
                sistema.append(mensaje.content)
            else:
                chat.append(mensaje.model_dump())
        return chat, "\n".join(sistema)

    def _system_kw(self, system: str) -> dict:
        """Anthropic rechaza un system vacío. Si no hay, no se manda el parámetro."""
        if not system:
            return {}
        return {"system": system}

    def _error(self, mensaje: str) -> ModelResponse:
        return ModelResponse(
            provider=Provider.ANTHROPIC,
            model=self.model,
            content="",
            error=mensaje,
        )
