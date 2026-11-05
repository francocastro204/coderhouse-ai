# Pre-entrega 5: agente ReAct con memoria

Un agente de pedidos decide solo qué herramienta llamar. Si le piden la cantidad y el total, tiene que llamar dos veces, porque ninguna herramienta trae los dos datos. La conversación queda en SQLite: con el mismo `thread_id`, la pregunta siguiente sigue el hilo.

La idea, en corto y con un diagrama, está en [resumen.md](resumen.md).

## Por qué Gemini

El enunciado nombra `ChatOpenAI` (`OPENAI_API_KEY`) o Anthropic. Esas APIs se cobran aparte y en este repo las claves están vacías. El modelo que corre es Gemini (`GEMINI_API_KEY`), con `bind_tools`. El grafo y las herramientas no dependen de la marca.

La memoria es SQLite. El enunciado nombra `SqliteSaver`. Esa clase no tiene métodos async, y el grafo corre con `ainvoke`, así que se usa `AsyncSqliteSaver`: el mismo archivo SQLite, en la variante async del mismo paquete.

## Cómo correrlo

Desde la raíz, con el entorno activo y `GEMINI_API_KEY` en el `.env`:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python unidad_5/pre_entrega/agente.py
```

Cada corrida borra `checkpoints.sqlite` y empieza la sesión `cliente-102` de cero. Ese archivo no se sube. La traza que sí se sube es [traza.json](traza.json).

El grafo se invoca con `recursion_limit` 10.

## Qué hace la prueba

1. «¿Cuántos pedidos tuvo el cliente 102 y cuál fue el total?» llama a `contar_pedidos` y a `sumar_pedidos`. La respuesta usa 3 pedidos y un total de 14500.
2. «¿y el último?», con el mismo `thread_id`, recuerda que se habla del cliente 102 y llama a `ultimo_pedido`. El último es el monitor P-933.

Si el id no existe, la herramienta devuelve un error en texto. El modelo puede pedir el id de nuevo, sin que el programa se caiga.

## Archivos

| Archivo | Rol |
| --- | --- |
| `agente.py` | `EstadoAgente` hereda de `MessagesState`. Nodos `agent` y `tools`, arista `tools_condition`, `AsyncSqliteSaver`. |
| `herramientas.py` | `contar_pedidos`, `sumar_pedidos` y `ultimo_pedido`. Base simulada. |
| `traza.json` | El ciclo ReAct de la última corrida. |
| `resumen.md` | La idea y el diagrama. |
