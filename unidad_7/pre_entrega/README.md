# Pre-entrega 7

La API recibe el pedido y devuelve un `job_id`. El grafo de la unidad 6 corre en un worker, con el estado en Redis. Si el analista dice que el reembolso corresponde, el hilo se pausa hasta que una persona lo apruebe. Cada corrida se ve en Phoenix.

## Cómo levantarlo

Desde la raíz del repo, con el entorno activo.

```bash
MODULOS=/opt/homebrew/opt/redis/lib/redis/modules
redis-server --port 6379 \
  --loadmodule $MODULOS/redisearch.so \
  --loadmodule $MODULOS/rejson.so
```

El checkpointer usa el índice de Redis y documentos JSON. Sin esos dos módulos, la API no arranca.

En otra terminal, Phoenix:

```bash
export PHOENIX_WORKING_DIR="$PWD/unidad_7/7.1/phoenix_data"
phoenix serve
```

El dashboard queda en http://localhost:6006. El proyecto de esta entrega se llama `pre-entrega-7`.

```bash
python -m uvicorn unidad_7.pre_entrega.app.main:app --host 0.0.0.0 --port 8000
```

Con Docker, solo Redis (la API sigue siendo el comando de arriba):

```bash
docker compose -f unidad_7/pre_entrega/docker-compose.yml up redis
```

## Una petición

```bash
curl -X POST localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Un cliente quiere devolver un producto de 14500 pesos a los 12 días. Busca la política de devoluciones y decide si corresponde el reembolso."}'

curl localhost:8000/tasks/<job_id>
```

El POST responde al instante con `PENDING`. Después el estado pasa a `RUNNING` y termina en `DONE`, `FAILED` o `WAITING_APPROVAL`.

Un caso que no corresponde (se pasó el plazo o el tope) cierra solo. Un caso que sí corresponde se frena: hay que aprobarlo.

```bash
curl -X POST localhost:8000/tasks/<job_id>/approve \
  -H "Content-Type: application/json" \
  -d '{"aprobado": false}'
```

`true` sigue a la síntesis. `false` deja `Reembolso rechazado por el revisor.` Si el worker se cae, el estado queda `FAILED` y el cliente no se queda esperando.

## Cinco a la vez

```bash
python unidad_7/pre_entrega/carga.py
```

Manda los cinco POST juntos. El worker los saca de la cola de a uno, para no pasarse del cupo de Gemini. El primero que queda en pausa se rechaza. El siguiente se aprueba.

En Phoenix, proyecto `pre-entrega-7`. Las capturas de esa corrida están en `screenshots/`:

- `latencia-p95.png` — Metrics, Trace latency, con la serie P95. Las raíces LangGraph de las cinco peticiones van de unos 27 s a 51 s; el p95 de esas raíces queda cerca de 50 s. El P50 de 12 ms del proyecto mezcla los `GET /tasks` del polling.
- `costo.png` — el costo que Phoenix calcula con los tokens. La corrida del 16/11 queda bajo $0.01.
- `traza.png` — una ejecución OK de 37.9 s, costo <$0.01, con LangGraph, el supervisor y el modelo.

Dos de las cinco pueden terminar `FAILED` con `TimeoutError` si Gemini corta la llamada. El estado queda escrito en Redis.
