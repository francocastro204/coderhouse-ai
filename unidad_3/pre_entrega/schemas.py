"""Contrato de la respuesta del RAG.

El modelo no devuelve un párrafo suelto. Devuelve este objeto:
el texto y los archivos de donde salió.
"""

from typing import List

from pydantic import BaseModel, Field


class RespuestaRAG(BaseModel):
    """Respuesta apoyada solo en los fragmentos recuperados."""

    respuesta: str = Field(
        description="Respuesta en español. Si el contexto no alcanza, exactamente: No lo sé.",
    )
    referencias: List[str] = Field(
        description="Nombres de archivo usados. Lista vacía si la respuesta es No lo sé.",
    )
