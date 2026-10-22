"""Los dos modelos que usa la unidad 2.

El principal es Gemini. Si Gemini falla (cupo, 503, red), la cadena
pasa sola a Hugging Face. Groq no entra: en este repo no hay clave de Groq.

Las claves se leen del .env que ya existe. No hay que crear variables nuevas.
"""

import logging
import os

from dotenv import load_dotenv
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

# El SDK de Gemini avisa que no recomienda "automatic function calling"
# en esta llamada. No lo usamos, así que ese aviso no aporta.
logging.getLogger("google_genai").setLevel(logging.ERROR)


def _clave(nombre: str, *alternativas: str) -> str:
    """Devuelve la primera variable de entorno que tenga texto."""
    for variable in (nombre, *alternativas):
        valor = os.getenv(variable, "").strip()
        if valor:
            return valor
    nombres = ", ".join((nombre, *alternativas))
    raise RuntimeError(f"Falta una API key en .env. Revisá: {nombres}")


def modelo_gemini() -> ChatGoogleGenerativeAI:
    """Chat de Google. El modelo por defecto es el que ya responde en la pre-entrega 1.

    gemini-1.5-flash está retirado en esta cuenta, por eso no se usa.
    """
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        google_api_key=_clave("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        temperature=0.2,
    )


def modelo_huggingface() -> ChatHuggingFace:
    """Chat de Hugging Face. Usa el mismo token y el mismo modelo que la pre-entrega 1.

    ChatHuggingFace, por debajo, llama a chat_completion: la misma ruta
    que el cliente de la pre-entrega. Si la cuenta no tiene créditos, esa
    ruta responde 402 y este respaldo no puede contestar.
    """
    repo_id = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    endpoint = HuggingFaceEndpoint(
        repo_id=repo_id,
        task="conversational",
        huggingfacehub_api_token=_clave("HF_TOKEN"),
        temperature=0.2,
        max_new_tokens=400,
    )
    return ChatHuggingFace(llm=endpoint)


def modelo_con_respaldo() -> Runnable:
    """Gemini primero. Si tira error, Hugging Face responde en su lugar."""
    return modelo_gemini().with_fallbacks([modelo_huggingface()])
