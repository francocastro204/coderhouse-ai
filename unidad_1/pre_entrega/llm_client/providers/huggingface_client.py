"""Cliente de Hugging Face.

Habla con la Inference API usando AsyncInferenceClient. Hugging Face es la
plataforma; el modelo concreto lo indica HF_MODEL. El token va en HF_TOKEN.

Un fallo de token, cupo o red vuelve como ModelResponse.error. El cupo
gratis es chico: un 429 es un resultado esperado, no un crash.
"""

from typing import AsyncGenerator, List

from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import HfHubHTTPError

from unidad_1.pre_entrega.llm_client.base import BaseLLMClient
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, ModelResponse, Provider


class HuggingFaceClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self._client = AsyncInferenceClient(token=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        try:
            response = await self._client.chat_completion(
                messages=[m.model_dump() for m in messages],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            texto = response.choices[0].message.content or ""
            return ModelResponse(provider=Provider.HUGGINGFACE, model=self.model, content=texto)
        except HfHubHTTPError as e:
            return self._error(f"Error de la API de Hugging Face: {e}")
        except Exception as e:
            return self._error(f"Error de la API de Hugging Face: {e}")

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        try:
            stream = await self._client.chat_completion(
                messages=[m.model_dump() for m in messages],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except (HfHubHTTPError, Exception) as e:
            yield f"\n[Error durante el streaming: {e}]"

    def _error(self, mensaje: str) -> ModelResponse:
        return ModelResponse(
            provider=Provider.HUGGINGFACE,
            model=self.model,
            content="",
            error=mensaje,
        )
