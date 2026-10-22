"""Esquemas de datos con Pydantic.

Este archivo define la forma de los datos que circulan por el cliente.
Sigue el notebook del curso: Provider, ChatMessage, LLMConfig y ModelResponse.

Para qué sirve:
- Validar el mensaje, el proveedor y los parámetros antes de llamar a una API.
- Guardar las API keys como secreto, para que no se impriman por accidente.
- Tener una sola forma de respuesta, incluido el error controlado.

Si un dato no cumple las reglas, Pydantic lanza un error claro y la
llamada a la API no se hace.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr, field_validator


class Provider(str, Enum):
    """Las empresas que este cliente sabe llamar.

    Hereda de str para que el valor se use como texto ("openai") y, a la
    vez, solo acepte estos nombres. Hugging Face es el extra, fuera del notebook.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"


class ChatMessage(BaseModel):
    """Un turno de la conversación.

    role dice quién habla. content es el texto.
    """

    role: str = Field(description="'user', 'assistant' o 'system'")
    content: str

    @field_validator("role")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        roles_permitidos = {"user", "assistant", "system"}
        if v not in roles_permitidos:
            raise ValueError(f"role debe ser uno de {roles_permitidos}, recibido: '{v}'")
        return v


class LLMConfig(BaseModel):
    """Qué proveedor usar, con qué modelo, y las claves que hagan falta.

    Cada clave es opcional: para hablar con Gemini no hace falta la de OpenAI.
    SecretStr evita que la clave aparezca si alguien imprime la config.
    temperature va de 0 a 2. max_tokens tiene que ser mayor que 0.
    """

    provider: Provider
    model: str
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None
    hf_token: Optional[SecretStr] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)


class ModelResponse(BaseModel):
    """Resultado de una llamada.

    content trae el texto del modelo. error trae el mensaje si la llamada
    falló (key inválida, red, rate limit). Si error tiene texto, el programa
    sigue vivo: no hubo crash.
    """

    provider: Provider
    model: str
    content: str
    error: Optional[str] = None
