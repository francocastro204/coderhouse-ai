import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any


# Mock del índice de Pinecone para testing
class MockPineconeIndex:
    async def upsert(self, vectors: List[Dict]):
        # Cada print es un lote. Con 5 documentos y batch_size 2 salen 2, 2 y 1.
        print(len(vectors))
        return {"upserted_count": len(vectors)}

    async def query(self, vector: List[float], top_k: int, filter: Dict = None):
        # El índice simulado no busca de verdad. Lo que se evalúa es el filtro.
        print(filter)
        return {"matches": []}


class IngestionPipeline:
    def __init__(self, index: MockPineconeIndex):
        self.index = index

    def create_metadata(self, doc_text: str, category: str, author: str) -> Dict[str, Any]:
        """
        Diccionario de metadatos con la misma forma para todos los documentos.
        Si un proceso usa otro nombre de campo, el filtro deja de encontrarlos.
        """
        return {
            "category": category,
            "author": author,
            "ingested_at": datetime.now().isoformat(),
            "char_count": len(doc_text),
        }

    async def process_and_upsert_batches(self, documents: List[Dict], batch_size: int = 100):
        """
        Parte la lista en lotes y hace un upsert por lote, no uno por documento.
        """
        total = 0
        for inicio in range(0, len(documents), batch_size):
            lote = documents[inicio : inicio + batch_size]
            vectors = [
                {
                    "id": str(uuid.uuid4()),
                    "values": [0.1] * 8,
                    "metadata": self.create_metadata(
                        documento["text"],
                        documento["category"],
                        documento["author"],
                    ),
                }
                for documento in lote
            ]
            await self.index.upsert(vectors)
            total += len(vectors)
        return total

    async def search_by_category(self, query_vector: List[float], category: str):
        """
        Busca similitud solo dentro de una categoría.
        $eq es el filtro rígido: category tiene que ser exactamente ese valor.
        """
        return await self.index.query(
            vector=query_vector,
            top_k=5,
            filter={"category": {"$eq": category}},
        )


async def main():
    index = MockPineconeIndex()
    pipeline = IngestionPipeline(index)

    # 2 legal, 2 hr y 1 de finanzas. Con lotes de 2, el último queda de 1.
    docs = [
        {"text": "Contrato de prestación de servicios.", "category": "legal", "author": "User1"},
        {"text": "Política de privacidad interna.", "category": "legal", "author": "User2"},
        {"text": "Manual de bienvenida al equipo.", "category": "hr", "author": "User3"},
        {"text": "Plan de vacaciones anuales.", "category": "hr", "author": "User4"},
        {"text": "Balance del primer trimestre.", "category": "finanzas", "author": "User5"},
    ]

    total = await pipeline.process_and_upsert_batches(docs, batch_size=2)
    print(total)
    resultado = await pipeline.search_by_category([0.1] * 8, "legal")
    print(resultado)


if __name__ == "__main__":
    asyncio.run(main())
