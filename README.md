# Cliente async unificado de LLMs

Este archivo es la puerta de entrada del repositorio. Quien lo clona tiene que poder entender qué es el proyecto, qué leer primero y, cuando el código esté listo, cómo ejecutarlo. La explicación larga vive en `docs/`. Acá queda el resumen y el modo de uso.

Pre-entrega 1 del curso de AI Engineering: un cliente en Python 3.12 que habla con varios modelos usando la misma interfaz, con llamadas async, streaming y validación con Pydantic.

## Para leer

- [docs/arquitectura.md](docs/arquitectura.md) — mapa del sistema.
- [docs/python-basico.md](docs/python-basico.md) — Python mínimo, y al final la comparación con JavaScript y TypeScript.
- [docs/glosario.md](docs/glosario.md) — qué significan LLM, temperatura, Pydantic, asyncio, LangChain, LangGraph y el resto de los términos del curso.

## Cómo probarlo

Con el entorno activo (el prompt muestra `(.venv)`):

```bash
python main.py
```

Pregunta "¿Qué es la entropía?" a OpenAI, Anthropic y Gemini, en modo normal y en streaming. Si falta una API key, ese proveedor se omite. Al final manda una key inválida a propósito: el programa tiene que seguir vivo.

## Estado

Clientes de OpenAI, Anthropic y Gemini listos, alineados con el notebook del curso. Hugging Face queda pendiente.

## Proveedores

| `LLM_PROVIDER` | Servicio | Variable |
| --- | --- | --- |
| `openai` | OpenAI | `OPENAI_API_KEY` |
| `anthropic` | Claude | `ANTHROPIC_API_KEY` |
| `gemini` | Google Gemini | `GEMINI_API_KEY` |
| `huggingface` | Hugging Face Inference | `HF_TOKEN` |

Copiá `.env.example` a `.env` y completá solo las keys que vayas a usar. El archivo `.env` no se sube a GitHub.
