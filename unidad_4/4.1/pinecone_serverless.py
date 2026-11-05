import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# La key vive en el .env de la raíz. load_dotenv la deja en el entorno.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# PINECONE_API_KEY tiene que estar en el .env de la raíz.
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

NAMESPACE = "dev-environment"


async def setup_vector_infrastructure(index_name: str, dimension: int):
    """
    Configura la infraestructura de Pinecone Serverless y realiza una carga inicial.
    """
    if not PINECONE_API_KEY:
        raise RuntimeError("Falta PINECONE_API_KEY en el .env de la raíz.")

    # 1. Inicializar el cliente de Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # 2. Crear el índice si no existe
    # Tip: Usa pc.list_indexes().names() para verificar existencia
    # Tip: Usa ServerlessSpec para definir la nube (aws) y región (us-east-1)
    # La dimensión tiene que ser la de los vectores. Acá es 1536, métrica coseno.
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        for _ in range(30):
            estado = pc.describe_index(index_name).status
            listo = estado["ready"] if isinstance(estado, dict) else estado.ready
            if listo:
                break
            await asyncio.sleep(2)
        else:
            raise RuntimeError(f"El índice {index_name} no quedó listo a tiempo.")

    # 3. Conectar al índice
    index = pc.Index(index_name)

    # 4. Implementar un Upsert de prueba usando un Namespace
    # Crea una pequeña lista de tuplas (id, vector, metadata)
    # El namespace separa estos vectores de prueba del resto del índice.
    # [0.1] * dimension arma un vector del largo que el índice espera.
    vectores = [
        ("vec1", [0.1] * dimension, {"topic": "infraestructura", "priority": "high"}),
        ("vec2", [0.2] * dimension, {"topic": "embeddings", "priority": "medium"}),
        ("vec3", [0.3] * dimension, {"topic": "namespaces", "priority": "low"}),
    ]
    index.upsert(vectors=vectores, namespace=NAMESPACE)

    # 5. Retornar las estadísticas del índice usando describe_index_stats()
    # Pinecone tarda unos segundos en contar los vectores recién subidos.
    for _ in range(10):
        estadisticas = index.describe_index_stats()
        namespaces = (
            estadisticas["namespaces"]
            if isinstance(estadisticas, dict)
            else estadisticas.namespaces
        )
        info = (namespaces or {}).get(NAMESPACE)
        cantidad = 0 if info is None else (
            info.get("vector_count", 0) if isinstance(info, dict) else info.vector_count
        )
        if cantidad >= len(vectores):
            return estadisticas
        await asyncio.sleep(2)
    return index.describe_index_stats()


if __name__ == "__main__":
    # Ejemplo con dimensión 1536 (OpenAI)
    estadisticas = asyncio.run(setup_vector_infrastructure("mi-indice-serverless", 1536))
    print(estadisticas)
