"""Agente ReAct con memoria de la conversación.

Pregunta el clima, llama a get_weather y, en un segundo mensaje del
mismo hilo, recuerda que se hablaba del tiempo. Otro thread_id empieza
de cero.

El enunciado instancia ChatOpenAI. Esa API se cobra. El modelo es Gemini,
el mismo de unidad_2/modelos.py. La forma del grafo no cambia.

Desde la raíz del repo:

    python unidad_5/5.3/agente.py
"""

import asyncio
import sys
from pathlib import Path
from typing import Annotated, TypedDict

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from unidad_2.modelos import modelo_gemini


class AgentState(TypedDict):
    # add_messages anexa. Sin ese reducer, cada nodo borraría el historial.
    messages: Annotated[list[BaseMessage], add_messages]


@tool
def get_weather(location: str) -> str:
    """Consulta el clima actual de una ciudad.

    Usala cuando pregunten qué tiempo hace en un lugar.
    Devuelve una frase con el clima de esa ciudad.
    """
    return f"Soleado, 22°C en {location}"


tools = [get_weather]
tool_node = ToolNode(tools)

# ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
# queda reemplazado por Gemini, que también publica las herramientas.
model = modelo_gemini().bind_tools(tools)


async def call_model(state: AgentState):
    response = await model.ainvoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", tools_condition)
workflow.add_edge("tools", "agent")

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def texto_de(mensaje) -> str:
    """Gemini a veces devuelve una lista de bloques. Acá queda una frase."""
    contenido = mensaje.content
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict):
                partes.append(bloque.get("text") or "")
            else:
                partes.append(str(bloque))
        return "".join(partes)
    return str(contenido)


def mostrar(titulo: str, resultado: dict) -> None:
    print(titulo)
    mensajes = resultado["messages"]
    desde = 0
    for indice, mensaje in enumerate(mensajes):
        if isinstance(mensaje, HumanMessage):
            desde = indice
    for mensaje in mensajes[desde:]:
        for llamada in getattr(mensaje, "tool_calls", None) or []:
            print(f"  herramienta: {llamada['name']} {llamada.get('args')}")
    print(texto_de(mensajes[-1]))
    print(f"  mensajes en el hilo: {len(mensajes)}")
    print()


async def main():
    thread_config = {"configurable": {"thread_id": "dev_test_01"}}

    print("--- Paso 1 ---")
    primero = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Qué tiempo hace en Madrid?")]},
        thread_config,
    )
    mostrar("Madrid, mismo hilo:", primero)

    print("--- Paso 2 ---")
    segundo = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Y en Londres?")]},
        thread_config,
    )
    mostrar("Londres, mismo hilo:", segundo)

    print("--- Otro hilo ---")
    otro = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Y en Londres?")]},
        {"configurable": {"thread_id": "sin_memoria"}},
    )
    mostrar("Londres, thread nuevo:", otro)


if __name__ == "__main__":
    asyncio.run(main())
