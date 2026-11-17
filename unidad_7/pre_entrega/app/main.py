"""API del orquestador. Recibe, encola y devuelve el job_id.

No corre el grafo adentro del request. El worker lo saca de Redis.
GET /tasks/{id} lee el estado. POST /tasks/{id}/approve reanuda
un hilo que quedó pausado.

Desde la raíz, con Redis y Phoenix ya levantados:

    python -m uvicorn unidad_7.pre_entrega.app.main:app --host 0.0.0.0 --port 8000
"""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import asyncio as aioredis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

from unidad_7.pre_entrega.app.graph import armar
from unidad_7.pre_entrega.app.observability import iniciar
from unidad_7.pre_entrega.app.worker import bucle, crear, leer, reanudar

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class Pedido(BaseModel):
    query: str


class Decision(BaseModel):
    aprobado: bool


@asynccontextmanager
async def vida(app: FastAPI):
    iniciar()
    app.state.redis = aioredis.from_url(
        REDIS_URL, decode_responses=True, socket_timeout=None
    )
    app.state.checkpointer = AsyncRedisSaver(redis_url=REDIS_URL)
    await app.state.checkpointer.asetup()
    app.state.graph = armar(app.state.checkpointer)
    app.state.fondo = set()
    tarea = asyncio.create_task(bucle(app.state.redis, app.state.graph))
    try:
        yield
    finally:
        tarea.cancel()
        await app.state.redis.aclose()


app = FastAPI(title="Tienda Lumen", lifespan=vida)


@app.post("/tasks")
async def crear_tarea(pedido: Pedido):
    return await crear(app.state.redis, pedido.query)


@app.get("/tasks/{job_id}")
async def estado(job_id: str):
    dato = await leer(app.state.redis, job_id)
    if dato is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return {"job_id": job_id, **dato}


@app.post("/tasks/{job_id}/approve")
async def aprobar(job_id: str, decision: Decision):
    dato = await leer(app.state.redis, job_id)
    if dato is None:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    if dato["status"] != "WAITING_APPROVAL":
        raise HTTPException(status_code=409, detail="Ese job no está esperando aprobación")
    tarea = asyncio.create_task(
        reanudar(app.state.redis, app.state.graph, job_id, decision.aprobado)
    )
    app.state.fondo.add(tarea)
    tarea.add_done_callback(app.state.fondo.discard)
    return {"job_id": job_id, "status": "RUNNING"}
