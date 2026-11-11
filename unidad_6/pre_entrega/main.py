"""Corre el orquestador con una pregunta que exige los dos especialistas.

La política de devolución está en la base del investigador.
Los días y el monto están en la pregunta.
El veredicto lo calcula el analista. El supervisor no puede saltarse a ninguno.

Desde la raíz del repo:

    python unidad_6/pre_entrega/main.py

El enunciado nombra Tavily o una vector DB. Acá la búsqueda es una
herramienta propia sobre una base chica, que es lo que el enunciado
también acepta. El modelo es Gemini: OpenAI y Anthropic se cobran aparte.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from unidad_6.pre_entrega.graph import construir, texto_de

CARPETA = Path(__file__).resolve().parent
TRAZA = CARPETA / "traza.json"
RECURSION_LIMIT = 20
PREGUNTA = (
    "Un cliente quiere devolver un producto de 14500 pesos a los 12 días. "
    "Busca la política de devoluciones y decide si corresponde el reembolso."
)


def fila(mensaje: Any) -> dict[str, Any]:
    datos: dict[str, Any] = {"rol": mensaje.type, "contenido": texto_de(mensaje)}
    nombre = getattr(mensaje, "name", None)
    if nombre:
        datos["name"] = nombre
    return datos


async def correr() -> dict[str, Any]:
    app = construir()
    resultado = await app.ainvoke(
        {
            "messages": [HumanMessage(content=PREGUNTA)],
            "aportes": [],
            "ruta": [],
            "pasos": 0,
            "next_agent": "",
            "task_completed": False,
            "instruccion": "",
        },
        {"recursion_limit": RECURSION_LIMIT},
    )
    respuesta = texto_de(resultado["messages"][-1])
    traza = {
        "pregunta": PREGUNTA,
        "recursion_limit": RECURSION_LIMIT,
        "ruta": resultado.get("ruta", []),
        "pasos_supervisor": resultado.get("pasos", 0),
        "task_completed": resultado.get("task_completed", False),
        "aportes": resultado.get("aportes", []),
        "respuesta": respuesta,
        "mensajes": [fila(mensaje) for mensaje in resultado["messages"]],
    }
    TRAZA.write_text(json.dumps(traza, ensure_ascii=False, indent=2), encoding="utf-8")
    return traza


def mostrar(traza: dict[str, Any]) -> None:
    print()
    print("Ruta:", " → ".join(traza["ruta"]))
    print()
    print(traza["respuesta"])
    print()
    print(f"Traza: {TRAZA.name}")


if __name__ == "__main__":
    mostrar(asyncio.run(correr()))
