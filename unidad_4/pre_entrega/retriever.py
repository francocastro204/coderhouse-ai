"""Recuperador híbrido: similitud en Pinecone más BM25.

BM25 mira las palabras (nombres como Task, Path o Depends). Pinecone mira
el sentido de la frase. EnsembleRetriever mezcla las dos listas.
"""

import warnings

warnings.filterwarnings("ignore", message=".*langchain-community.*")

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from unidad_4.pre_entrega.config import (
    CLAVE_TEXTO,
    INDICE,
    NAMESPACE,
    TOP_K,
    embeddings,
)
from unidad_4.pre_entrega.ingest import contar_namespace
from unidad_4.pre_entrega.setup_index import asegurar_indice, cliente


def documentos_del_indice() -> list[Document]:
    """Baja el texto guardado en la metadata. BM25 no vive dentro de Pinecone."""
    indice = cliente().Index(INDICE)
    ids: list[str] = []
    token = None
    try:
        while True:
            respuesta = indice.list_paginated(
                namespace=NAMESPACE,
                limit=100,
                pagination_token=token,
            )
            for item in respuesta.vectors or []:
                ids.append(item.id)
            paginacion = respuesta.pagination
            token = None if paginacion is None else getattr(paginacion, "next", None)
            if not token:
                break

        documentos = []
        for inicio in range(0, len(ids), 100):
            lote = indice.fetch(ids=ids[inicio : inicio + 100], namespace=NAMESPACE)
            vectores = lote["vectors"] if isinstance(lote, dict) else lote.vectors
            for vector in vectores.values():
                metadata = (
                    dict(vector["metadata"])
                    if isinstance(vector, dict)
                    else dict(vector.metadata or {})
                )
                texto = str(metadata.pop(CLAVE_TEXTO, ""))
                documentos.append(Document(page_content=texto, metadata=metadata))
    except Exception as error:
        raise RuntimeError("No se pudieron leer los fragmentos de Pinecone.") from error
    return documentos


class RAGSystem:
    """Une la búsqueda semántica y la léxica, y devuelve 5 fragmentos."""

    def __init__(self) -> None:
        asegurar_indice()
        if contar_namespace() == 0:
            raise RuntimeError(
                "El namespace está vacío. Primero corré "
                "python -m unidad_4.pre_entrega.ingest"
            )
        bm25 = BM25Retriever.from_documents(documentos_del_indice())
        bm25.k = TOP_K
        vectorial = PineconeVectorStore(
            index=cliente().Index(INDICE),
            embedding=embeddings(),
            namespace=NAMESPACE,
            text_key=CLAVE_TEXTO,
        ).as_retriever(search_kwargs={"k": TOP_K})
        # El mismo peso para las dos listas. La fusión es Reciprocal Rank Fusion.
        self.ensemble = EnsembleRetriever(
            retrievers=[vectorial, bm25],
            weights=[0.5, 0.5],
        )

    def buscar(self, consulta: str) -> list[Document]:
        """Devuelve como máximo los 5 documentos mejor rankeados."""
        try:
            return self.ensemble.invoke(consulta)[:TOP_K]
        except Exception as error:
            raise RuntimeError("No se pudo buscar en el recuperador híbrido.") from error
