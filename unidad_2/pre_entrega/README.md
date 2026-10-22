# Pre-entrega 2: pipeline de procesamiento validado

Recibe un párrafo y devuelve un objeto validado: tecnologías, nivel de criticidad (`baja`, `media` o `alta`) y un resumen técnico.

## Por qué Gemini

El enunciado nombra `ChatOpenAI` (`OPENAI_API_KEY`) o `ChatAnthropic` (`ANTHROPIC_API_KEY`). Esas APIs se cobran aparte y en este repo las dos claves están vacías. El modelo que corre es `ChatGoogleGenerativeAI`, con el cupo gratis de AI Studio. Si Gemini falla, `with_fallbacks` pasa a Hugging Face.

En `unidad_2/modelos.py` quedó comentado cómo se armaría `ChatOpenAI` o `ChatAnthropic` si hubiera saldo. La cadena no cambiaría: `with_structured_output`, `with_retry` y `with_fallbacks` no dependen de la marca. `chain.py` sigue siendo `prompt | model`.

## Cómo correrlo

Desde la raíz del repo, con el entorno activo y `GEMINI_API_KEY` en el `.env` (ese archivo no se sube):

```bash
source .venv/bin/activate
python -m unidad_2.pre_entrega.chain
```

El script de prueba manda un texto de checkout con FastAPI, Redis y PostgreSQL.

## Archivos

| Archivo | Rol |
| --- | --- |
| `schemas.py` | Contrato Pydantic. La lista de tecnologías no puede venir vacía. |
| `chain.py` | Prompt, cadena LCEL, `process_text` y el script de prueba. |
| `../modelos.py` | Gemini y el respaldo de Hugging Face. Lo comparte el ejercicio opcional. |

La cadena es `prompt | model`. El modelo ya incluye `with_structured_output(EntidadesTecnicas)`, un respaldo y `with_retry(stop_after_attempt=3)`.

## Ejemplo de salida

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "Sistema de checkout que utiliza FastAPI para la lógica, PostgreSQL para persistencia y Redis para la gestión de sesiones, presentando un punto único de fallo crítico en Redis."
}
```
