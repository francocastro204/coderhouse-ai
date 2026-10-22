"""Cliente de Google Gemini.

Habla con la API de Gemini usando el SDK google-genai en modo async
(client.aio). Gemini no usa el rol "assistant": el asistente se llama
"model", y el system prompt va en la configuración, separado del chat.

La clave sale de GEMINI_API_KEY (o GOOGLE_API_KEY, el nombre del notebook).
Un fallo de la API vuelve como ModelResponse.error.
"""

from typing import AsyncGenerator, List, Optional

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from unidad_1.pre_entrega.llm_client.base import BaseLLMClient
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, ModelResponse, Provider


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self._client = genai.Client(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _convertir_mensajes(
        self, messages: List[ChatMessage]
    ) -> tuple[list[types.Content], Optional[str]]:
        """Separa el system prompt y traduce 'assistant' al rol 'model'."""
        contents: list[types.Content] = []
        system_instruction = None
        for mensaje in messages:
            if mensaje.role == "system":
                system_instruction = mensaje.content
            else:
                rol_gemini = "model" if mensaje.role == "assistant" else "user"
                contents.append(
                    types.Content(role=rol_gemini, parts=[types.Part(text=mensaje.content)])
                )
        return contents, system_instruction

    def _config(self, system_instruction: Optional[str]) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            system_instruction=system_instruction,
            # Esta pre-entrega no usa herramientas. Sin esto, el SDK avisa
            # que generate_content no es el lugar para function calling.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            contents, system_instruction = self._convertir_mensajes(messages)
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=self._config(system_instruction),
            )
            return ModelResponse(
                provider=Provider.GEMINI,
                model=self.model,
                content=response.text or "",
            )
        except genai_errors.APIError as e:
            return self._error(f"Error de la API de Gemini: {e}")
        except Exception as e:
            return self._error(f"Error de la API de Gemini: {e}")

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            contents, system_instruction = self._convertir_mensajes(messages)
            stream = await self._client.aio.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=self._config(system_instruction),
            )
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[Error durante el streaming: {e}]"

    def _error(self, mensaje: str) -> ModelResponse:
        return ModelResponse(
            provider=Provider.GEMINI,
            model=self.model,
            content="",
            error=mensaje,
        )
