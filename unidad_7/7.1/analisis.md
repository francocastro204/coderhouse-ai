# Instrumentación y análisis de trazas con Phoenix

Orquestador de la unidad 6 (Tienda Lumen) contra Phoenix local, proyecto `tienda-lumen`, en http://localhost:6006.

El modelo es `gemini-flash-lite-latest`. En las trazas el proveedor lo nombra `gemini-3.5-flash-lite`. La búsqueda pasa por Chroma (colección `politicas-lumen`).

## Las cinco consultas

Las cinco cerraron con la regla de la base: hasta 10 días y hasta 20000 pesos.

| Caso | Decisión | ¿Apoyada en la política? |
| --- | --- | --- |
| 14500 pesos, 12 días | No. Pasó el plazo de 10. | Sí |
| 8000 pesos, 3 días | Sí. Entra en plazo y en tope. | Sí |
| 25000 pesos, 5 días | No. El monto pasa el tope de 20000. | Sí |
| 18000 pesos, 10 días | Sí. 10 días entra y 18000 no pasa el tope. | Sí |
| 5000 pesos, 15 días | No. 15 días pasa el plazo de 10. | La decisión sí. Una frase no. |

La frase que no está apoyada está en la quinta: «El aporte del investigador sobre el estado sin uso falta». El documento recuperado sí dice que el producto no tiene que tener uso. La síntesis inventó que ese dato no había llegado. El no al reembolso sigue siendo correcto, porque 15 es mayor que 10.

## Jerarquía que se ve en el dashboard

Una consulta que termina bien queda así:

```text
LangGraph
  supervisor → ChatGoogleGenerativeAI
  investigador → agent → ChatGoogleGenerativeAI
               → buscar_documentos → VectorStoreRetriever
  analista → agent → ChatGoogleGenerativeAI
           → validar_reembolso
  validar
  sintesis → ChatGoogleGenerativeAI
```

`chroma.buscar_politica` es el span propio de la base. Adentro está `EmbedContent` (el embedding). En esta sesión ese span salió como traza raíz, al lado del grafo, no como hijo de `buscar_documentos`. El tiempo de la base igual está dentro del grafo, en `VectorStoreRetriever`.

## Qué tardó más

El razonamiento más largo que sí terminó es el de 25000 pesos a los 5 días. Traza `891c187a`. El grafo duró 57,6 s.

El span suelto más lento de esa traza es una llamada al modelo del analista: `ChatGoogleGenerativeAI`, 13,4 s, 496 tokens. No es la recuperación.

En esa misma traza:

- las 8 llamadas al modelo suman 56,6 s
- `VectorStoreRetriever` tardó 0,46 s
- `validar_reembolso` tardó 2,8 ms

La recuperación más lenta de las consultas que sí cerraron fue 1,35 s (8000 pesos, 3 días). Sigue siendo mucho menos que cualquier llamada larga al modelo.

## Red y procesamiento

La espera de red es `ChatGoogleGenerativeAI` y `EmbedContent`. Las dos salen de la máquina hacia la API de Gemini.

El procesamiento local es `validar_reembolso` (0,3 ms a 2,8 ms) y el ruteo (`ruta_supervisor`, cerca de 1 ms).

Casi todo `VectorStoreRetriever` es la llamada de embeddings, no la búsqueda en Chroma. `EmbedContent` va de 0,4 s a 1,3 s. Cuando el span de la base falla a propósito, sin llegar a embeddings, dura unos 3 ms.

## Tokens y costo del razonamiento más largo

Traza `891c187a`, ocho llamadas al modelo, sin sumar el span duplicado de Google (`AsyncGenerateContent` repite los mismos tokens):

- entrada: 2014
- salida: 300
- total: 2314

La sesión corrió en el free tier. El 429 de Gemini lo dice explícito, así que esta corrida no se cobró.

Si esos tokens se pagaran al precio publicado de `gemini-3.5-flash-lite` (0,30 USD por millón de entrada y 2,50 USD por millón de salida, [precios de Gemini](https://ai.google.dev/gemini-api/docs/pricing)):

- entrada: 2014 / 1.000.000 × 0,30 = 0,00060 USD
- salida: 300 / 1.000.000 × 2,50 = 0,00075 USD
- total estimado: 0,0014 USD

La consulta de 5000 pesos a los 15 días hizo un trabajo parecido (1969 de entrada y 287 de salida) y terminó en 21,3 s. La de 57,6 s no razonó más: se quedó esperando la API.

## El fallo a propósito

Después de las cinco, la búsqueda levantó `RuntimeError: Base de políticas no disponible` antes de tocar Chroma.

En la traza `14948c78` (8,9 s) el error sube así:

```text
LangGraph ERROR
  investigador ERROR
    tools ERROR
      buscar_documentos ERROR
```

El modelo del investigador había respondido bien (6,4 s, status OK). El fallo está en la herramienta, no en la generación. El span `chroma.buscar_politica` quedó en ERROR con el mismo mensaje, en unos 3 ms.

## Cómo bajarlo

Cada caso bueno hace 8 llamadas al modelo en serie. Tres son del supervisor, y el camino ya está fijado: primero el investigador, después el analista, después cerrar. En la traza larga esas tres llamadas fueron 2,2 s, 11,5 s y 1,2 s.

Sacar el modelo del ruteo y dejar la regla que ya elige al que falta corta esa espera y unos 200 tokens de entrada por llamada. La política es un texto fijo: cachear el embedding evita repetir `EmbedContent` en cada pregunta.
