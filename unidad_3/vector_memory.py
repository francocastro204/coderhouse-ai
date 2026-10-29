import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional


class VectorMemoryManager:
    def __init__(self, persist_path: str, collection_name: str):
        # La base queda en disco. Al cerrar el programa, los documentos siguen ahí.
        self.client = chromadb.PersistentClient(path=persist_path)
        # get_or_create abre la colección si ya existe y la crea si no.
        # DefaultEmbeddingFunction convierte el texto en vector, siempre con el mismo modelo.
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
        )

    def upsert_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Implementa el método upsert para evitar errores por IDs duplicados.
        """
        # Si el id ya existe, se reemplaza el texto. No se agrega una copia.
        # Si el disco o Chroma fallan, el error sale con un mensaje claro.
        # Un reintento repetiría esta llamada un par de veces ante un fallo pasajero.
        try:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        except Exception as error:
            raise RuntimeError("No se pudieron guardar los documentos.") from error

    def semantic_search(
        self,
        query_text: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda por similitud.
        Retorna los documentos más cercanos al query_text.
        """
        # where filtra por metadato, por ejemplo {"source": "tech_blog"}.
        # Chroma también acepta $eq, $ne, $in, $and y $or para afinar el filtro.
        # Si no viene filtro, no se lo pasa a query.
        try:
            consulta = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                **({"where": where} if where is not None else {}),
            )
            documentos = consulta["documents"][0]
            metadatos = consulta["metadatas"][0]
            distancias = consulta["distances"][0]
        except Exception as error:
            raise RuntimeError("No se pudo buscar en la memoria vectorial.") from error
        return [
            {"document": documento, "metadata": metadato, "distance": distancia}
            for documento, metadato, distancia in zip(documentos, metadatos, distancias)
        ]

    def delete_by_id(self, ids: List[str]) -> None:
        # Borra por id. El resto de la colección queda en disco.
        try:
            self.collection.delete(ids=ids)
        except Exception as error:
            raise RuntimeError("No se pudieron borrar los documentos.") from error


if __name__ == "__main__":
    manager = VectorMemoryManager("./chroma_db", "knowledge_base")
    manager.upsert_documents(
        ["doc1", "doc2", "doc3"],
        [
            "Python 3.12 introduce mejoras en asyncio y tipos.",
            "Las bases de datos vectoriales son clave para la memoria de largo plazo en IA.",
            "FastAPI permite crear APIs asíncronas en Python.",
        ],
        [{"source": "news"}, {"source": "tech_blog"}, {"source": "tech_blog"}],
    )
    print(manager.semantic_search("mejoras en python"))
    print(manager.semantic_search("memoria de IA", where={"source": "tech_blog"}))
    manager.delete_by_id(["doc2"])
    print(manager.collection.count())
