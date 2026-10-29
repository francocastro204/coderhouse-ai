"""Índice de Pinecone y embeddings compartidos por la pre-entrega 4.

El enunciado nombra embeddings de OpenAI de 1536 dimensiones. Acá el
vector lo genera Gemini, recortado a esas mismas 1536. El índice y la
búsqueda tienen que usar el mismo número. Si no, Pinecone rechaza el alta.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA / "data"
GOLDEN = CARPETA / "golden_set.json"

load_dotenv(RAIZ / ".env")

# 1536 es el tamaño que el enunciado pide para text-embedding-3-small.
# gemini-embedding-001 puede devolver ese tamaño con output_dimensionality.
DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
MODELO_EMBEDDING = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
INDICE = os.getenv("INDEX_NAME", "coderhouse-unidad-4")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "biblioteca")
NUBE = os.getenv("PINECONE_CLOUD", "aws")
REGION = os.getenv("PINECONE_REGION", "us-east-1")

# Punto medio del rango que pide el enunciado (500 a 800 tokens).
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
TOP_K = 5

# Campo de metadata donde Pinecone guarda el texto del fragmento.
CLAVE_TEXTO = "texto"


def clave_pinecone() -> str:
    """Lee la key. Si falta, el mensaje dice dónde ponerla."""
    clave = os.getenv("PINECONE_API_KEY", "").strip()
    if not clave:
        raise RuntimeError(
            "Falta PINECONE_API_KEY en el .env de la raíz. "
            "Se crea gratis en https://app.pinecone.io y no se sube a GitHub."
        )
    return clave


def embeddings() -> GoogleGenerativeAIEmbeddings:
    """Mismo modelo y misma dimensión para indexar y para buscar."""
    clave = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not clave:
        raise RuntimeError("Falta GEMINI_API_KEY en el .env de la raíz.")
    return GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDING,
        google_api_key=clave,
        output_dimensionality=DIMENSION,
    )
