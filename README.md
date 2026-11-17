# coderhouse-ai

Repo del curso de AI Engineering. Cada unidad tiene dos entregas: la pre-entrega y el ejercicio opcional. Lo que está en la raíz no es una entrega: es lo que comparten las dos.

## Mapa

```text
coderhouse-ai/
├── README.md                 ← este mapa
├── requirements.txt          ← librerías de todo el repo
├── .env                      ← tus API keys. No se sube a GitHub
├── .env.example              ← la misma lista, sin secretos
├── docs/                     ← apuntes: arquitectura, Python básico, glosario
├── unidad_1/
│   ├── pre_entrega/          ← cliente async. Ya está corregida
│   │   ├── main.py
│   │   └── llm_client/
│   └── ejercicio_opcional/   ← orquestador simulado con asyncio
│       ├── orquestador.py
│       └── entregable.pdf
├── unidad_2/
│   ├── modelos.py            ← Gemini y Hugging Face, compartidos
│   ├── ejercicio_opcional/   ← cadena LCEL simple
│   └── pre_entrega/          ← extrae tecnologías de un texto
├── unidad_3/
│   ├── ejercicio_opcional/   ← similitud coseno, se entrega en PDF
│   └── pre_entrega/          ← RAG local con Chroma
├── unidad_4/
│   ├── 4.1/                  ← índice Serverless y namespace
│   ├── 4.2/                  ← lotes y filtro por metadata
│   └── pre_entrega/          ← RAG en Pinecone, híbrido y métricas
├── unidad_5/
│   ├── 5.1/                  ← grafo de soporte, con ciclo
│   ├── 5.2/                  ← herramienta con contrato Pydantic
│   ├── 5.3/                  ← ReAct con checkpointer en memoria
│   └── pre_entrega/          ← agente de pedidos, SQLite y traza
├── unidad_6/
    ├── 6.1/                  ← diseño: quejas de Twitter, topología jerárquica
    ├── 6.2/                  ← supervisor que elige Analista, Escritor o fin
    ├── 6.3/                  ← estado compartido, cada nodo escribe su campo
    └── pre_entrega/          ← supervisor, investigador y analista
└── unidad_7/
    ├── 7.1/                  ← trazas del orquestador en Phoenix local
    └── 7.2/                  ← FastAPI encola en Redis y devuelve un job_id
```

## Qué es cada cosa

**Pre-entrega 1.** Un cliente de Python que habla con OpenAI, Anthropic, Gemini y Hugging Face usando la misma interfaz. Las llamadas son async. Si falta una key o la key es inválida, el programa lo informa y sigue. El código está en `unidad_1/pre_entrega/`.

**Ejercicio opcional 1.** No llama a ninguna API. Simula tres modelos en paralelo, corta a los 2 segundos y después deja correr solo 2 de 10 con un semáforo.

**Ejercicio opcional 2.** Una cadena LCEL: prompt, modelo y parser. Pregunta qué es LangChain. Gemini responde. Si Gemini falla, prueba Hugging Face.

**Pre-entrega 2.** Otra cadena LCEL. De un texto saca las tecnologías, un nivel de criticidad (baja, media, alta) y un resumen. El resultado es un objeto de Pydantic, no un párrafo suelto. El detalle, el ejemplo de JSON y cómo correrla están en [unidad_2/pre_entrega/README.md](unidad_2/pre_entrega/README.md).

**Ejercicio opcional 3.** Compara significado y coincidencia de palabras. El entregable es el PDF en `unidad_3/ejercicio_opcional/`.

**Pre-entrega 3.** RAG local. Indexa unas notas en Chroma y responde solo con esos fragmentos. Cómo correrla está en [unidad_3/pre_entrega/README.md](unidad_3/pre_entrega/README.md).

**Pre-entrega 4.** RAG en Pinecone. Sube notas técnicas a un índice Serverless, busca con vectores y BM25, y mide Precision@5 y Recall@5. Cómo replicar el índice está en [unidad_4/pre_entrega/README.md](unidad_4/pre_entrega/README.md).

**Pre-entrega 5.** Un agente de pedidos decide qué herramienta llamar, puede llamar más de una, y recuerda la sesión en SQLite. Cómo correrlo está en [unidad_5/pre_entrega/README.md](unidad_5/pre_entrega/README.md).

**Pre-entrega 6.** Un supervisor manda la pregunta primero a quien busca la política y después a quien calcula si el caso entra. Cómo correrlo está en [unidad_6/pre_entrega/README.md](unidad_6/pre_entrega/README.md).

**`modelos.py`.** Arma Gemini y Hugging Face una sola vez. Las dos partes de la unidad 2 lo importan, por eso no está metido dentro de una sola entrega.

**`.env`.** Las claves viven acá, en la raíz. Todas las unidades leen el mismo archivo.

**`requirements.txt`.** La lista de librerías, como el `package.json`. La de la pre-entrega 1 está en `unidad_1/pre_entrega/requirements.txt` y la de la raíz la incluye, más LangChain de la unidad 2.

## Cómo correrlo

Desde la raíz, con el entorno activo (el prompt muestra `(.venv)`):

```bash
source .venv/bin/activate

python -m unidad_1.pre_entrega.main
python unidad_1/ejercicio_opcional/orquestador.py
python -m unidad_2.ejercicio_opcional.refactorizacion_lcel_asincrono
python -m unidad_2.pre_entrega.chain
python -m unidad_3.pre_entrega.chain
python -m unidad_4.pre_entrega.ingest
python -m unidad_4.pre_entrega.evaluate
```

La pre-entrega 1 pregunta "¿Qué es la entropía?". OpenAI y Anthropic se saltan si esas keys están vacías.

Cada carpeta de entrega tiene un `resumen.md`: la idea en corto y un diagrama. Los dos scripts sueltos de la unidad 3 están en [unidad_3/ejercicios.md](unidad_3/ejercicios.md).

## Para leer

- [docs/arquitectura.md](docs/arquitectura.md) — cómo está armado el cliente de la pre-entrega 1.
- [docs/python-basico.md](docs/python-basico.md) — Python mínimo, y al final la comparación con JavaScript y TypeScript.
- [docs/glosario.md](docs/glosario.md) — LLM, temperatura, Pydantic, asyncio, LangChain y el resto.
