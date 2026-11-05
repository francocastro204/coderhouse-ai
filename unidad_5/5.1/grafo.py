"""Asistente de soporte técnico multinivel.

El grafo no llama a ningún modelo. Search_Knowledge simula el RAG:
en una duda normal resuelve al segundo intento; si el texto dice
"imposible", nunca resuelve y a los 3 intentos escala a un humano.

Desde la raíz del repo:

    python unidad_5/5.1/grafo.py
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class SupportState(TypedDict):
    """Memoria que viaja por el grafo. Cada nodo devuelve solo lo que cambia."""

    messages: Annotated[list[BaseMessage], add_messages]
    is_escalated: bool
    attempts: int
    solved: bool


def triage(state: SupportState) -> dict:
    """Clasifica la duda. No la resuelve."""
    print("[triage] duda clasificada")
    return {"messages": [AIMessage(content="Duda clasificada. Paso a buscar.")]}


def search_knowledge(state: SupportState) -> dict:
    """Simula el RAG. Suma un intento y, si puede, marca la duda como resuelta."""
    intento = state["attempts"] + 1
    consulta = ""
    for mensaje in state["messages"]:
        if isinstance(mensaje, HumanMessage):
            consulta = mensaje.content
            break
    resuelto = "imposible" not in consulta.lower() and intento >= 2
    print(f"[search] intento {intento} -> {'resuelto' if resuelto else 'sin resultado'}")
    return {
        "attempts": intento,
        "solved": resuelto,
        "messages": [
            AIMessage(content=f"Intento {intento}: {'solución' if resuelto else 'sin resultado'}")
        ],
    }


def evaluator(state: SupportState) -> dict:
    """No cambia el estado. La decisión la toma la arista condicional."""
    print(
        f"[evaluator] solved={state['solved']} attempts={state['attempts']}"
    )
    return {}


def human_support(state: SupportState) -> dict:
    """Escala el caso. Este es el único nodo que pone is_escalated en True."""
    print("[human] caso escalado a soporte humano")
    return {
        "is_escalated": True,
        "messages": [AIMessage(content="Caso escalado a un humano.")],
    }


def route(state: SupportState) -> str:
    """Desde Evaluator: terminar, escalar o volver a buscar."""
    if state["solved"]:
        return "end"
    if state["attempts"] >= 3:
        return "escalate"
    return "retry"


def construir():
    grafo = StateGraph(SupportState)
    grafo.add_node("triage", triage)
    grafo.add_node("search_knowledge", search_knowledge)
    grafo.add_node("evaluator", evaluator)
    grafo.add_node("human_support", human_support)
    grafo.add_edge(START, "triage")
    grafo.add_edge("triage", "search_knowledge")
    grafo.add_edge("search_knowledge", "evaluator")
    grafo.add_conditional_edges(
        "evaluator",
        route,
        {
            "end": END,
            "escalate": "human_support",
            "retry": "search_knowledge",
        },
    )
    grafo.add_edge("human_support", END)
    return grafo.compile()


def estado_inicial(duda: str) -> SupportState:
    return {
        "messages": [HumanMessage(content=duda)],
        "is_escalated": False,
        "attempts": 0,
        "solved": False,
    }


def main() -> None:
    app = construir()

    print("Caso 1. Se resuelve al segundo intento.")
    final = app.invoke(estado_inicial("No puedo iniciar sesión"))
    print(
        f"attempts={final['attempts']} solved={final['solved']} "
        f"is_escalated={final['is_escalated']}"
    )

    print()
    print("Caso 2. Nunca hay solución. A los 3 intentos escala.")
    final = app.invoke(estado_inicial("Esto es imposible de resolver"))
    print(
        f"attempts={final['attempts']} solved={final['solved']} "
        f"is_escalated={final['is_escalated']}"
    )


if __name__ == "__main__":
    main()
