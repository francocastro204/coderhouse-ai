"""La API recibe el pedido y devuelve un job al instante.

El trabajo de 5 segundos lo hace un worker, en el mismo proceso,
leyendo la cola de Redis. El cliente pregunta el estado por el job_id.

Antes, en otra terminal:

    redis-server --port 6379

Desde la raíz, con el entorno activo:

    python unidad_7/7.2/api.py
"""

import asyncio
import json
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import asyncio as aioredis

REDIS_URL = "redis://localhost:6379"
QUEUE_NAME = "tasks_queue"
STATUS_PREFIX = "status:"

app = FastAPI()
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


class TaskRequest(BaseModel):
    query: str


def _clave(job_id: str) -> str:
    return f"{STATUS_PREFIX}{job_id}"


async def _guardar(job_id: str, estado: dict) -> None:
    await redis_client.set(_clave(job_id), json.dumps(estado))


async def _leer(job_id: str) -> dict | None:
    crudo = await redis_client.get(_clave(job_id))
    if crudo is None:
        return None
    return json.loads(crudo)


@app.post("/process")
async def create_task(request: TaskRequest):
    """Guarda pending y recién ahí encola. Si no, el cliente puede ver un 404."""
    job_id = str(uuid.uuid4())
    await _guardar(
        job_id,
        {"status": "pending", "query": request.query, "result": None},
    )
    await redis_client.rpush(QUEUE_NAME, job_id)
    return {"job_id": job_id, "status": "pending"}


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """Devuelve el JSON del job. Si la clave no está, 404."""
    estado = await _leer(job_id)
    if estado is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return estado


async def task_worker():
    """Saca un job, lo marca processing, espera 5 segundos y lo cierra."""
    print("Worker iniciado...", flush=True)
    while True:
        tomado = await redis_client.blpop(QUEUE_NAME, timeout=0)
        if not tomado:
            continue
        job_id = tomado[1]
        estado = await _leer(job_id)
        if estado is None:
            continue
        estado["status"] = "processing"
        await _guardar(job_id, estado)
        await asyncio.sleep(5)
        estado["status"] = "completed"
        estado["result"] = f"Procesado: {estado['query']}"
        await _guardar(job_id, estado)


# El worker arranca junto con la API, en el mismo event loop que usa uvicorn
@app.on_event("startup")
async def start_worker():
    asyncio.create_task(task_worker())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
