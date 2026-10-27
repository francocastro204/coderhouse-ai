# Pre-entrega 3: recuperación semántica local (RAG)

El script lee unos textos de AndesPay, los corta en fragmentos, los guarda en Chroma en esta carpeta y responde preguntas usando solo esos fragmentos. Si la respuesta no está, dice «No lo sé».

El enunciado nombra OpenAI. Acá el chat y los embeddings son de Gemini (`GEMINI_API_KEY`), el mismo cupo gratis del resto del repo. Indexar y buscar usan el mismo modelo (`gemini-embedding-001`). Si fueran dos modelos distintos, la búsqueda no tendría sentido.

## Cómo correrlo

Desde la raíz, con el entorno activo y `GEMINI_API_KEY` en el `.env`:

```bash
source .venv/bin/activate
python -m unidad_3.pre_entrega.ingest
python -m unidad_3.pre_entrega.chain
```

`chain` vuelve a ingestar solo si la colección está vacía. La base queda en `unidad_3/pre_entrega/vectorstore/` y no se sube a GitHub.

La primera corrida hace dos preguntas. Una está en los textos (Redis caído). La otra no (el precio de un plan).

## Archivos

| Archivo | Rol |
| --- | --- |
| `data/` | Cuatro notas en Markdown. El dataset de ejemplo. |
| `ingest.py` | Lee `data/`, corta a 500 tokens con 50 de solape y guarda en Chroma. |
| `chain.py` | `get_rag_response`: busca 4 fragmentos, llama a Gemini y valida con Pydantic. |
| `schemas.py` | `respuesta` y `referencias`. |
| `store.py` | El modelo de embeddings y la carpeta de Chroma, compartidos por los dos scripts. |
