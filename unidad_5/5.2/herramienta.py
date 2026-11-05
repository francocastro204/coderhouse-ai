"""Herramienta de búsqueda para un agente.

El modelo no ejecuta esta función. Pide el nombre y los argumentos.
Pydantic revisa esos argumentos y, si sirven, el programa llama a la base.

Desde la raíz del repo:

    python unidad_5/5.2/herramienta.py
"""

import asyncio
from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field, ValidationError


class SearchInput(BaseModel):
    """Contrato de entrada. El modelo tiene que llenar estos campos."""

    query: str = Field(..., description="Texto a buscar en la base de conocimiento.")
    limit: int = Field(
        3,
        description="Cantidad de fragmentos a devolver. Entre 1 y 10.",
        ge=1,
        le=10,
    )


class MockVectorDB:
    async def similarity_search(self, query: str, k: int):
        return [f"Resultado para {query}"]


db = MockVectorDB()


@tool(args_schema=SearchInput)
async def search_knowledge_base(query: str, limit: int = 3) -> List[str] | str:
    """Busca fragmentos en la base de conocimiento interna.

    Usala cuando la pregunta sea sobre políticas, procedimientos o
    documentación de la empresa, por ejemplo vacaciones o soporte.
    Devuelve una lista de textos. Si la base falla, devuelve el error
    como texto para que el modelo pueda explicarlo.
    """
    try:
        return await db.similarity_search(query, k=limit)
    except Exception as error:
        return f"No se pudo buscar en la base: {error}"


if __name__ == "__main__":
    print(search_knowledge_base.name, search_knowledge_base.args)
    print(
        asyncio.run(
            search_knowledge_base.ainvoke(
                {"query": "políticas de vacaciones", "limit": 2}
            )
        )
    )
    try:
        asyncio.run(
            search_knowledge_base.ainvoke(
                {"query": "políticas de vacaciones", "limit": 50}
            )
        )
    except ValidationError as error:
        print(error)
