"""AsyncLLMManager: elige el proveedor y esconde el SDK.

Es la fachada del paquete. Recibe un LLMConfig y construye OpenAI,
Anthropic, Gemini o Hugging Face. Quien pregunta llama a generate() o
generate_stream() y no necesita saber qué empresa responde.

Si falta la API key del proveedor elegido, avisa con un ValueError claro
antes de llamar a la red.
"""

from typing import AsyncGenerator, List

from llm_client.base import BaseLLMClient
from llm_client.providers.anthropic_client import AnthropicClient
from llm_client.providers.gemini_client import GeminiClient
from llm_client.providers.huggingface_client import HuggingFaceClient
from llm_client.providers.openai_client import OpenAIClient
from llm_client.schemas import ChatMessage, LLMConfig, ModelResponse, Provider


class AsyncLLMManager:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: BaseLLMClient = self._crear_cliente()

    def _crear_cliente(self) -> BaseLLMClient:
        if self.config.provider == Provider.OPENAI:
            if not self.config.openai_api_key:
                raise ValueError("Falta openai_api_key en la configuración")
            return OpenAIClient(
                api_key=self.config.openai_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        if self.config.provider == Provider.ANTHROPIC:
            if not self.config.anthropic_api_key:
                raise ValueError("Falta anthropic_api_key en la configuración")
            return AnthropicClient(
                api_key=self.config.anthropic_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        if self.config.provider == Provider.GEMINI:
            if not self.config.google_api_key:
                raise ValueError("Falta google_api_key en la configuración")
            return GeminiClient(
                api_key=self.config.google_api_key.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        if self.config.provider == Provider.HUGGINGFACE:
            if not self.config.hf_token:
                raise ValueError("Falta hf_token en la configuración")
            return HuggingFaceClient(
                api_key=self.config.hf_token.get_secret_value(),
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        raise ValueError(f"Proveedor no soportado: {self.config.provider}")

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        return await self._client.generate(messages)

    async def generate_stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        async for chunk in self._client.generate_stream(messages):
            yield chunk
