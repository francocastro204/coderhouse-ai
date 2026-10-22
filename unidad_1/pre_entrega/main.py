"""Script de prueba de la pre-entrega.

Carga el .env y hace la pregunta "¿Qué es la entropía?" en este orden:
OpenAI, Anthropic, Gemini y Hugging Face. Cada uno en modo normal y en streaming.
Si un proveedor no tiene API key, lo salta y sigue con el siguiente.
Al final manda una key inválida a propósito, para comprobar que el
programa no se cae.

Se corre desde la raíz del repo, con el entorno virtual activo:
    source .venv/bin/activate
    python -m unidad_1.pre_entrega.main
"""

import asyncio
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv
from pydantic import SecretStr

from unidad_1.pre_entrega.llm_client.manager import AsyncLLMManager
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage, LLMConfig, Provider

PREGUNTA = [
    ChatMessage(role="user", content="¿Qué es la entropía? Respondé en 2 líneas."),
]


def clave(*nombres: str) -> SecretStr | None:
    """Devuelve la primera variable de entorno que tenga texto."""
    for nombre in nombres:
        valor = os.environ.get(nombre, "").strip()
        if valor:
            return SecretStr(valor)
    return None


async def probar(etiqueta: str, config: LLMConfig) -> None:
    manager = AsyncLLMManager(config)
    resultado = await manager.generate(PREGUNTA)
    if resultado.error:
        print(f"{etiqueta}: {resultado.error}")
    else:
        print(f"{etiqueta}: {resultado.content}")

    print(f"\n{etiqueta} streaming:")
    async for pedazo in manager.generate_stream(PREGUNTA):
        print(pedazo, end="", flush=True)
    print("\n")


async def main() -> None:
    load_dotenv(RAIZ / ".env")

    pruebas = [
        (
            "OpenAI",
            Provider.OPENAI,
            os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            clave("OPENAI_API_KEY"),
            "openai_api_key",
        ),
        (
            "Anthropic",
            Provider.ANTHROPIC,
            os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            clave("ANTHROPIC_API_KEY"),
            "anthropic_api_key",
        ),
        (
            "Gemini",
            Provider.GEMINI,
            os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            clave("GEMINI_API_KEY", "GOOGLE_API_KEY"),
            "google_api_key",
        ),
        (
            "Hugging Face",
            Provider.HUGGINGFACE,
            os.environ.get("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
            clave("HF_TOKEN"),
            "hf_token",
        ),
    ]

    for etiqueta, provider, model, api_key, campo in pruebas:
        if api_key is None:
            print(f"{etiqueta}: sin API key en el .env, se omite.\n")
            continue
        config = LLMConfig(
            provider=provider,
            model=model,
            temperature=0.7,
            max_tokens=200,
            **{campo: api_key},
        )
        await probar(etiqueta, config)

    print("Prueba con una API key inválida (no tiene que tirar el programa):")
    config_rota = LLMConfig(
        provider=Provider.OPENAI,
        model="gpt-4o-mini",
        openai_api_key=SecretStr("sk-key-invalida-a-proposito"),
        temperature=0.7,
        max_tokens=50,
    )
    resultado = await AsyncLLMManager(config_rota).generate(PREGUNTA)
    print("El programa siguió vivo.")
    print("Error capturado:", resultado.error)


if __name__ == "__main__":
    asyncio.run(main())
