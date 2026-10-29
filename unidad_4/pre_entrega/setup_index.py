"""Crea el índice Serverless de Pinecone si todavía no existe.

Desde la raíz del repo, con el entorno activo:

    python -m unidad_4.pre_entrega.setup_index
"""

import time

from pinecone import Pinecone, ServerlessSpec

from unidad_4.pre_entrega.config import (
    DIMENSION,
    INDICE,
    NUBE,
    REGION,
    clave_pinecone,
)


def cliente() -> Pinecone:
    return Pinecone(api_key=clave_pinecone())


def asegurar_indice() -> None:
    """Abre el índice o lo crea en modo Serverless.

    Si ya existe con otra dimensión, se detiene. Subir vectores de otro
    tamaño a ese índice es el error de mismatch que el enunciado marca.
    """
    pc = cliente()
    try:
        if not pc.has_index(INDICE):
            pc.create_index(
                name=INDICE,
                dimension=DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud=NUBE, region=REGION),
                vector_type="dense",
            )
        descripcion = pc.describe_index(INDICE)
    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError("No se pudo preparar el índice de Pinecone.") from error

    if int(descripcion.dimension) != DIMENSION:
        raise RuntimeError(
            f"El índice {INDICE} tiene dimensión {descripcion.dimension} "
            f"y los embeddings usan {DIMENSION}. Hay que usar el mismo número."
        )

    for _ in range(30):
        estado = pc.describe_index(INDICE).status
        listo = estado["ready"] if isinstance(estado, dict) else estado.ready
        if listo:
            return
        time.sleep(2)
    raise RuntimeError(f"El índice {INDICE} no quedó listo a tiempo.")


def main() -> None:
    asegurar_indice()
    print(f"Índice listo: {INDICE} ({DIMENSION} dimensiones, {NUBE}/{REGION})")


if __name__ == "__main__":
    main()
