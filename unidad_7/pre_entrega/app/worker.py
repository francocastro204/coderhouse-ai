"""Cola y estado de cada job, en Redis.

Primero se escribe PENDING. Después se encola. Si el grafo se cae,
el estado pasa a FAILED. Si el reembolso saldría, queda WAITING_APPROVAL
hasta que /approve reanude el mismo thread_id.
"""

import json
import uuid
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from unidad_6.pre_entrega.graph import texto_de

COLA = "preentrega7:queue"
PREFIJO = "preentrega7:status:"


def clave(job_id: str) -> str:
    return f"{PREFIJO}{job_id}"


async def guardar(redis, job_id: str, estado: dict) -> None:
    await redis.set(clave(job_id), json.dumps(estado, ensure_ascii=False))


async def leer(redis, job_id: str) -> dict | None:
    crudo = await redis.get(clave(job_id))
    if crudo is None:
        return None
    return json.loads(crudo)


async def crear(redis, query: str) -> dict:
    job_id = str(uuid.uuid4())
    estado = {
        "status": "PENDING",
        "query": query,
        "result": None,
        "error": None,
        "pregunta": None,
    }
    await guardar(redis, job_id, estado)
    await redis.rpush(COLA, job_id)
    return {"job_id": job_id, "status": "PENDING"}


def _entrada(query: str) -> dict:
    return {
        "messages": [HumanMessage(content=query)],
        "aportes": [],
        "ruta": [],
        "pasos": 0,
        "next_agent": "",
        "task_completed": False,
        "instruccion": "",
    }


def _config(job_id: str) -> dict:
    return {"configurable": {"thread_id": job_id}, "recursion_limit": 20}


def _pregunta(snap) -> str | None:
    for tarea in getattr(snap, "tasks", None) or []:
        for corte in getattr(tarea, "interrupts", None) or []:
            valor = getattr(corte, "value", corte)
            if isinstance(valor, dict):
                return str(valor.get("pregunta") or valor)
            return str(valor)
    if getattr(snap, "next", None):
        return "Hace falta una persona para seguir."
    return None


def _respuesta(snap) -> str:
    mensajes = (getattr(snap, "values", None) or {}).get("messages") or []
    for mensaje in reversed(mensajes):
        if getattr(mensaje, "type", "") == "ai":
            return texto_de(mensaje).strip()
    return ""


async def _marcar_failed(redis, job_id: str, estado: dict, error: Exception) -> None:
    estado["status"] = "FAILED"
    estado["error"] = f"{error.__class__.__name__}: {error}"
    await guardar(redis, job_id, estado)
    print(f"job {job_id} FAILED {estado['error']}", flush=True)


async def procesar(redis, graph, job_id: str) -> None:
    estado = await leer(redis, job_id)
    if estado is None:
        return
    estado["status"] = "RUNNING"
    estado["error"] = None
    await guardar(redis, job_id, estado)
    try:
        if estado["query"] == "provocar-fallo":
            raise RuntimeError("Fallo de prueba")
        config = _config(job_id)
        try:
            await graph.ainvoke(_entrada(estado["query"]), config)
        except GraphInterrupt:
            pass
        snap = await graph.aget_state(config)
        if _pregunta(snap) and snap.next:
            estado["status"] = "WAITING_APPROVAL"
            estado["pregunta"] = _pregunta(snap)
            estado["result"] = None
            await guardar(redis, job_id, estado)
            print(f"job {job_id} WAITING_APPROVAL", flush=True)
            return
        estado["status"] = "DONE"
        estado["result"] = _respuesta(snap)
        estado["pregunta"] = None
        await guardar(redis, job_id, estado)
        print(f"job {job_id} DONE", flush=True)
    except Exception as error:
        await _marcar_failed(redis, job_id, estado, error)


async def reanudar(redis, graph, job_id: str, aprobado: bool) -> None:
    estado = await leer(redis, job_id)
    if estado is None:
        return
    estado["status"] = "RUNNING"
    estado["error"] = None
    await guardar(redis, job_id, estado)
    try:
        config = _config(job_id)
        try:
            await graph.ainvoke(Command(resume="si" if aprobado else "no"), config)
        except GraphInterrupt:
            pass
        snap = await graph.aget_state(config)
        if _pregunta(snap) and snap.next:
            estado["status"] = "WAITING_APPROVAL"
            estado["pregunta"] = _pregunta(snap)
            await guardar(redis, job_id, estado)
            return
        estado["status"] = "DONE"
        estado["result"] = _respuesta(snap)
        estado["pregunta"] = None
        await guardar(redis, job_id, estado)
        print(f"job {job_id} DONE tras la aprobación", flush=True)
    except Exception as error:
        await _marcar_failed(redis, job_id, estado, error)


async def bucle(redis, graph) -> None:
    print("Worker iniciado...", flush=True)
    while True:
        try:
            tomado: Any = await redis.blpop([COLA], timeout=0)
        except Exception as error:
            print(f"worker no pudo leer la cola: {error}", flush=True)
            await asyncio.sleep(1)
            continue
        if not tomado:
            continue
        try:
            await procesar(redis, graph, tomado[1])
        except Exception as error:
            print(f"worker cortó el job: {error}", flush=True)
