# 7.1 Observabilidad: Phoenix y LangSmith

Un LLM puede responder 200 OK y estar mal. La observabilidad reconstruye qué pasó con trazas, spans y evaluaciones.

## Qué recordar

- Traza: el viaje entero, desde la pregunta hasta la respuesta.
- Span: un paso de esa traza. Llamada al modelo, búsqueda en la base o herramienta. Se anidan. La traza es el árbol.
- Run: en LangSmith, una ejecución de un Runnable de LangChain.
- Si el total tarda 10 segundos, el span dice si se fue en la API, en la base vectorial o en un bucle del grafo.
- p95 es el tiempo del 5% más lento. Un promedio de 3 s con un p95 de 45 s es un problema de experiencia.
- En RAG se miden tres cosas. Fidelidad: la respuesta sale solo del contexto recuperado. Usar conocimiento interno, aunque sea cierto afuera, es alucinación. Relevancia: la respuesta contesta la pregunta. Precisión de contexto: los documentos traídos servían.
- Si la respuesta es mala y el span de recuperación vino vacío, el arreglo es el retriever. Cambiar el prompt ahí optimiza el componente equivocado.
- Phoenix es abierto, local y habla OpenTelemetry (OpenInference). Sirve con LangChain, LlamaIndex o el SDK directo. El dashboard queda en `localhost:6006`.
- LangSmith va con LangChain y LangGraph. Con dos variables de entorno registra solo. Desde la UI se edita el prompt y se vuelve a correr. Arma datasets con trazas de producción.
- El evaluador LLM es una alerta temprana. La lógica fija sigue en tests, y los casos críticos los mira una persona.
- Cada traza lleva la versión del prompt. Un cambio de una palabra alcanza para alucinar.

## En la corrida de Tienda Lumen

- El span lento fue `ChatGoogleGenerativeAI` (red). `VectorStoreRetriever` tardó menos de 1,5 s. `validar_reembolso` tardó milisegundos (procesamiento local).
- La quinta respuesta decidió bien con la política y además inventó que faltaba el dato de «sin uso». Eso es una falla de fidelidad: el documento sí lo traía.
- Cortar la base dejó el span de la herramienta en ERROR. El modelo anterior quedó OK. El status del modelo no alcanza para ver el fallo.
