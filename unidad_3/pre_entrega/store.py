"""Base vectorial de la pre-entrega 3.

Los documentos y las preguntas se convierten con el mismo modelo de
embeddings. Si no, la distancia entre vectores no significa nada.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA / "data"
VECTORSTORE = CARPETA / "vectorstore"
COLECCION = "andespay"
TOP_K = 4

load_dotenv(RAIZ / ".env")


def embeddings() -> GoogleGenerativeAIEmbeddings:
    """Mismo modelo para indexar y para buscar.

    No se fija task_type: al indexar LangChain usa RETRIEVAL_DOCUMENT
    y al buscar usa RETRIEVAL_QUERY. El modelo es el mismo.
    """
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        google_api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
    )


def abrir() -> Chroma:
    """Abre la colección en disco. Si la carpeta no existe, Chroma la crea."""
    VECTORSTORE.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLECCION,
        embedding_function=embeddings(),
        persist_directory=str(VECTORSTORE),
    )


def splitter() -> RecursiveCharacterTextSplitter:
    """Corta en trozos de 500 tokens, con 50 de solapamiento."""
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=50,
    )


def leer_documentos() -> list[Document]:
    """Lee los .md de data/. El nombre del archivo queda en la metadata."""
    documentos = []
    for ruta in sorted(DATOS.glob("*.md")):
        documentos.append(
            Document(
                page_content=ruta.read_text(encoding="utf-8"),
                metadata={"fuente": ruta.name},
            )
        )
    if not documentos:
        raise RuntimeError(f"No hay archivos .md en {DATOS}")
    return documentos


def ingestar(forzar: bool = False) -> Chroma:
    """Llena Chroma si la colección está vacía.

    Si ya hay fragmentos, no vuelve a llamar al modelo de embeddings.
    """
    base = abrir()
    if base._collection.count() > 0 and not forzar:
        return base
    if forzar and base._collection.count() > 0:
        base.delete_collection()
        base = abrir()
    trozos = splitter().split_documents(leer_documentos())
    base.add_documents(trozos)
    return base
