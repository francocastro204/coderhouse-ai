"""Agente de pedidos con ciclo ReAct y memoria en SQLite.

La primera pregunta pide cantidad y total. Cada dato vive en una
herramienta distinta, así que el modelo tiene que llamar al menos dos.
La segunda, en el mismo thread_id, pregunta por el último pedido.

El enunciado nombra ChatOpenAI. Esa API se cobra. El modelo es Gemini.
La memoria es AsyncSqliteSaver: SqliteSaver no corre con ainvoke.

Desde la raíz del repo:

    python unidad_5/pre_entrega/agente.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
# SqliteSaver no implementa aget_tuple. Con ainvoke hay que usar
# AsyncSqliteSaver: la misma base SQLite, en versión async.
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from unidad_2.modelos import modelo_gemini
from unidad_5.pre_entrega.herramientas import TOOLS

CARPETA = Path(__file__).resolve().parent
DB = CARPETA / "checkpoints.sqlite"
TRAZA = CARPETA / "traza.json"
THREAD_ID = "cliente-102"
RECURSION_LIMIT = 10

PREGUNTA_1 = "¿Cuántos pedidos tuvo el cliente 102 y cuál fue el total?"
PREGUNTA_2 = "¿y el último?"

SISTEMA = (
    "Sos un asistente de pedidos. No inventes cantidades ni montos. "
    "Si un dato no está en el historial, llamá a la herramienta que lo tiene. "
    "contar_pedidos no trae el total. sumar_pedidos no trae la cantidad. "
    "ultimo_pedido no sirve para ninguna de las dos. "
    "Si una herramienta devuelve un error, pedí el id correcto y no sigas calculando. "
    "Respondé en español, en una frase, con los números que devolvieron las herramientas."
)


class EstadoAgente(MessagesState):
    """El historial vive en messages. add_messages ya viene de MessagesState."""


tool_node = ToolNode(TOOLS)
model = modelo_gemini().bind_tools(TOOLS)


async def call_model(state: EstadoAgente) -> dict[str, list[Any]]:
    response = await model.ainvoke([SystemMessage(content=SISTEMA), *state["messages"]])
    return {"messages": [response]}


def construir(memoria: AsyncSqliteSaver):
    workflow = StateGraph(EstadoAgente)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")
    return workflow.compile(checkpointer=memoria)


def texto_de(mensaje: Any) -> str:
    contenido = mensaje.content
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict):
                partes.append(str(bloque.get("text") or ""))
            else:
                partes.append(str(bloque))
        return "".join(partes)
    return str(contenido)


def fila(mensaje: Any) -> dict[str, Any]:
    datos: dict[str, Any] = {
        "rol": mensaje.type,
        "contenido": texto_de(mensaje),
    }
    llamadas = getattr(mensaje, "tool_calls", None) or []
    if llamadas:
        datos["tool_calls"] = [
            {"name": llamada["name"], "args": llamada.get("args")} for llamada in llamadas
        ]
    nombre = getattr(mensaje, "name", None)
    if nombre:
        datos["name"] = nombre
    return datos


def guardar_traza(mensajes: list[Any]) -> None:
    traza = {
        "thread_id": THREAD_ID,
        "recursion_limit": RECURSION_LIMIT,
        "preguntas": [PREGUNTA_1, PREGUNTA_2],
        "mensajes": [fila(mensaje) for mensaje in mensajes],
    }
    TRAZA.write_text(json.dumps(traza, ensure_ascii=False, indent=2), encoding="utf-8")


def mostrar(titulo: str, resultado: dict[str, Any]) -> None:
    mensajes = resultado["messages"]
    desde = 0
    for indice, mensaje in enumerate(mensajes):
        if isinstance(mensaje, HumanMessage):
            desde = indice
    print(titulo)
    for mensaje in mensajes[desde:]:
        for llamada in getattr(mensaje, "tool_calls", None) or []:
            print(f"  herramienta: {llamada['name']} {llamada.get('args')}")
        if getattr(mensaje, "type", "") == "tool":
            print(f"  resultado: {texto_de(mensaje)}")
    print(texto_de(mensajes[-1]))
    print()


async def main() -> None:
    for sobra in DB.parent.glob("checkpoints.sqlite*"):
        sobra.unlink()

    config = {
        "configurable": {"thread_id": THREAD_ID},
        "recursion_limit": RECURSION_LIMIT,
    }
    async with AsyncSqliteSaver.from_conn_string(str(DB)) as memoria:
        app = construir(memoria)
        print("--- Paso 1 ---")
        primero = await app.ainvoke(
            {"messages": [HumanMessage(content=PREGUNTA_1)]},
            config,
        )
        mostrar(PREGUNTA_1, primero)

        print("--- Paso 2 ---")
        segundo = await app.ainvoke(
            {"messages": [HumanMessage(content=PREGUNTA_2)]},
            config,
        )
        mostrar(PREGUNTA_2, segundo)
        guardar_traza(segundo["messages"])

    llamadas = [
        llamada["name"]
        for mensaje in segundo["messages"]
        for llamada in (getattr(mensaje, "tool_calls", None) or [])
    ]
    print(f"Herramientas usadas: {llamadas}")
    print(f"Traza: {TRAZA.name}")


if __name__ == "__main__":
    asyncio.run(main())
