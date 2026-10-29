# Pre-entrega 4: RAG en Pinecone

El módulo sube unas notas técnicas a un índice Serverless de Pinecone, busca con un recuperador híbrido (vector + BM25) y mide Precision@5 y Recall@5.

El enunciado nombra `OPENAI_API_KEY` y embeddings `text-embedding-3-small` de 1536 dimensiones. Esa API se cobra aparte, así que la key queda vacía. Los vectores los genera Gemini (`gemini-embedding-001`), recortados a **1536**, el mismo tamaño del índice. Indexar y buscar usan ese mismo modelo. Si el número no coincide, Pinecone rechaza el alta.

## Cómo replicar el índice

1. Crear una cuenta gratis en [Pinecone](https://app.pinecone.io) y copiar la API key.
2. En el `.env` de la raíz, completar `PINECONE_API_KEY`. `GEMINI_API_KEY` ya se usa en las unidades anteriores. `INDEX_NAME` puede quedar en `coderhouse-unidad-4`.
3. Desde la raíz, con el entorno activo:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unidad_4.pre_entrega.setup_index
python -m unidad_4.pre_entrega.ingest
python -m unidad_4.pre_entrega.evaluate
```

`setup_index` crea el índice Serverless en `aws` / `us-east-1` solo si no existe, con métrica coseno y 1536 dimensiones. `ingest` corta los Markdown de `data/` a 600 tokens (solape 80) y los sube al namespace `biblioteca`. Si ese namespace ya tiene vectores, no vuelve a llamar al modelo. `ingest --forzar` lo vacía y lo arma de nuevo.

La primera corrida de embeddings puede tardar un poco. El índice no se commitea: vive en Pinecone.

## Qué se guarda en cada vector

El texto del fragmento va en la metadata (`texto`), no en otra base. Al lado van:

| Campo | Ejemplo |
| --- | --- |
| `documento_id` | `asyncio` |
| `fuente` | `asyncio.md` |
| `pagina` | `1` |
| `categoria` | `concurrencia` |
| `etiquetas` | `["asyncio", "task"]` |

El namespace `biblioteca` separa estos documentos de cualquier otro uso del mismo índice.

## Búsqueda y métricas

`RAGSystem.buscar` devuelve 5 fragmentos. Pinecone ordena por similitud del vector. BM25 ordena por las palabras (Task, Path, Depends, Handler). `EnsembleRetriever` mezcla las dos listas con el mismo peso.

`evaluate.py` lee `golden_set.json`: 5 preguntas, cada una con el `documento_id` que debería aparecer.

- **Recall@5:** 1 si ese documento está entre los 5, 0 si no. El promedio es la fracción de preguntas resueltas.
- **Precision@5:** de esos 5, qué fracción pertenece al documento esperado. Cada nota se parte en dos fragmentos, así que el techo de una pregunta es 0.40 (2 de 5) si entran los dos. Si entra uno solo, Precision@5 queda en 0.20 y Recall@5 sigue en 1.

El resumen se imprime en la consola.

## Archivos

| Archivo | Rol |
| --- | --- |
| `setup_index.py` | Crea el índice Serverless si no existe y comprueba la dimensión. |
| `ingest.py` | Lee `data/`, corta y sube a Pinecone con la metadata. |
| `retriever.py` | `RAGSystem`: Pinecone + BM25 en un `EnsembleRetriever`. |
| `evaluate.py` | Precision@5 y Recall@5 contra el golden set. |
| `golden_set.json` | Cinco preguntas y el documento que tienen que recuperar. |
| `data/` | Ocho notas de la biblioteca estándar y de FastAPI y Pydantic. |
| `config.py` | Dimensión, namespace, modelo y rutas, compartidos. |
