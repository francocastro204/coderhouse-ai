"""Carga los textos de data/ en Pinecone.

El texto del fragmento queda en la metadata, junto con la fuente, la
página, la categoría y las etiquetas. Así la búsqueda no necesita otra
base para recuperar el párrafo.

Desde la raíz del repo, con el entorno activo:

    python -m unidad_4.pre_entrega.ingest
    python -m unidad_4.pre_entrega.ingest --forzar
"""

import argparse

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from unidad_4.pre_entrega.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CLAVE_TEXTO,
    DATOS,
    INDICE,
    NAMESPACE,
    embeddings,
)
from unidad_4.pre_entrega.setup_index import asegurar_indice, cliente

# Cada archivo es un documento del golden set. El id es el nombre, sin .md.
CATALOGO = {
    "asyncio": {"categoria": "concurrencia", "etiquetas": ["asyncio", "task"]},
    "pathlib": {"categoria": "archivos", "etiquetas": ["pathlib", "path"]},
    "typing": {"categoria": "tipos", "etiquetas": ["typing", "protocol"]},
    "pydantic": {"categoria": "validacion", "etiquetas": ["pydantic", "basemodel"]},
    "fastapi": {"categoria": "web", "etiquetas": ["fastapi", "dependencias"]},
    "logging": {"categoria": "observabilidad", "etiquetas": ["logging", "handler"]},
    "dataclasses": {"categoria": "tipos", "etiquetas": ["dataclasses", "asdict"]},
    "contextlib": {"categoria": "recursos", "etiquetas": ["contextlib", "exitstack"]},
}


def leer_documentos() -> list[Document]:
    """Lee los .md de data/. La metadata ya trae id, fuente y categoría."""
    documentos = []
    for ruta in sorted(DATOS.glob("*.md")):
        documento_id = ruta.stem
        if documento_id not in CATALOGO:
            raise RuntimeError(f"Falta la categoría de {ruta.name} en CATALOGO.")
        ficha = CATALOGO[documento_id]
        documentos.append(
            Document(
                page_content=ruta.read_text(encoding="utf-8"),
                metadata={
                    "documento_id": documento_id,
                    "fuente": ruta.name,
                    "categoria": ficha["categoria"],
                    "etiquetas": ficha["etiquetas"],
                },
            )
        )
    if not documentos:
        raise RuntimeError(f"No hay archivos .md en {DATOS}")
    return documentos


def partir(documentos: list[Document]) -> tuple[list[Document], list[str]]:
    """Corta a 600 tokens. La página es el número de fragmento dentro del archivo."""
    cortador = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    trozos = cortador.split_documents(documentos)
    paginas: dict[str, int] = {}
    ids = []
    for trozo in trozos:
        documento_id = trozo.metadata["documento_id"]
        paginas[documento_id] = paginas.get(documento_id, 0) + 1
        trozo.metadata["pagina"] = paginas[documento_id]
        ids.append(f"{documento_id}-{paginas[documento_id]}")
    return trozos, ids


def contar_namespace() -> int:
    """Cuántos vectores hay en el namespace de esta entrega."""
    indice = cliente().Index(INDICE)
    try:
        estadisticas = indice.describe_index_stats()
    except Exception as error:
        raise RuntimeError("No se pudo leer el índice de Pinecone.") from error
    namespaces = (
        estadisticas["namespaces"]
        if isinstance(estadisticas, dict)
        else estadisticas.namespaces
    )
    if not namespaces or NAMESPACE not in namespaces:
        return 0
    info = namespaces[NAMESPACE]
    if isinstance(info, dict):
        return int(info.get("vector_count", 0))
    return int(info.vector_count)


def ingestar(forzar: bool = False) -> int:
    """Sube los fragmentos. Si el namespace ya tiene datos, no vuelve a cobrar embeddings."""
    asegurar_indice()
    if contar_namespace() > 0 and not forzar:
        return contar_namespace()

    indice = cliente().Index(INDICE)
    if forzar:
        try:
            indice.delete(delete_all=True, namespace=NAMESPACE)
        except Exception as error:
            raise RuntimeError("No se pudo vaciar el namespace.") from error

    trozos, ids = partir(leer_documentos())
    almacen = PineconeVectorStore(
        index=indice,
        embedding=embeddings(),
        namespace=NAMESPACE,
        text_key=CLAVE_TEXTO,
    )
    try:
        almacen.add_documents(trozos, ids=ids)
    except Exception as error:
        raise RuntimeError("No se pudieron subir los fragmentos a Pinecone.") from error
    return len(ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta de la pre-entrega 4")
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Borra el namespace y vuelve a indexar.",
    )
    args = parser.parse_args()
    cantidad = ingestar(forzar=args.forzar)
    print(f"Fragmentos en {INDICE}/{NAMESPACE}: {cantidad}")


if __name__ == "__main__":
    main()
