"""Manda 5 pedidos juntos y espera a que cada uno salga de la cola.

Si un caso queda esperando a una persona, el primero se rechaza
y el siguiente se aprueba. Así se ven las dos salidas del HITL.

Desde la raíz, con la API ya en el puerto 8000:

    python unidad_7/pre_entrega/carga.py
"""

import asyncio
import json
import urllib.request

BASE = "http://127.0.0.1:8000"
PEDIDOS = [
    "Un cliente quiere devolver un producto de 14500 pesos a los 12 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 8000 pesos a los 3 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 25000 pesos a los 5 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 18000 pesos a los 10 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 5000 pesos a los 15 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
]


def pedir(method: str, path: str, body: dict | None = None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


async def esperar(job_id: str, finales: set[str]) -> dict:
    for _ in range(150):
        estado = await asyncio.to_thread(pedir, "GET", f"/tasks/{job_id}")
        if estado["status"] in finales:
            return estado
        await asyncio.sleep(2)
    return {"job_id": job_id, "status": "TIMEOUT", "result": None, "error": None}


async def uno(query: str) -> dict:
    creado = await asyncio.to_thread(pedir, "POST", "/tasks", {"query": query})
    print(f"encolado {creado['job_id'][:8]}", flush=True)
    estado = await esperar(creado["job_id"], {"DONE", "FAILED", "WAITING_APPROVAL"})
    print(f"{estado['job_id'][:8]} {estado['status']}", flush=True)
    return estado


async def cerrar_pausa(estado: dict, aprobado: bool) -> None:
    print(f"apruebo {estado['job_id'][:8]} aprobado={aprobado}", flush=True)
    await asyncio.to_thread(
        pedir,
        "POST",
        f"/tasks/{estado['job_id']}/approve",
        {"aprobado": aprobado},
    )
    final = await esperar(estado["job_id"], {"DONE", "FAILED"})
    print(f"{estado['job_id'][:8]} {final['status']} {final.get('result') or final.get('error')}", flush=True)


async def main() -> None:
    resultados = await asyncio.gather(*(uno(pedido) for pedido in PEDIDOS))
    pausados = [estado for estado in resultados if estado["status"] == "WAITING_APPROVAL"]
    for indice, estado in enumerate(pausados):
        await cerrar_pausa(estado, aprobado=indice > 0)


if __name__ == "__main__":
    asyncio.run(main())
