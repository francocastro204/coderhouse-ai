"""Reembolso que se frena si el monto es grande.

Menos de 1000 sigue solo. 1000 o más se pausa con interrupt
hasta que una persona dice si o no. El estado vive en memoria.

Desde la raíz, con el entorno activo:

    python unidad_7/7.2/aprobacion.py
"""

from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Estado(TypedDict):
    pedido: str
    monto: float
    aprobado: bool
    resultado: str


def evaluar(estado: Estado) -> dict:
    return {}


def aprobacion_humana(estado: Estado) -> dict:
    if estado["monto"] < 1000:
        return {"aprobado": True}
    decision = interrupt(
        {
            "pregunta": f"¿Aprobás el reembolso de {estado['monto']} USD?",
            "pedido": estado["pedido"],
        }
    )
    return {"aprobado": decision == "si"}


def ejecutar(estado: Estado) -> dict:
    if estado["aprobado"]:
        return {"resultado": "Reembolso ejecutado"}
    return {"resultado": "Reembolso rechazado por el revisor"}


def construir():
    builder = StateGraph(Estado)
    builder.add_node("evaluar", evaluar)
    builder.add_node("aprobacion_humana", aprobacion_humana)
    builder.add_node("ejecutar", ejecutar)
    builder.add_edge(START, "evaluar")
    builder.add_edge("evaluar", "aprobacion_humana")
    builder.add_edge("aprobacion_humana", "ejecutar")
    builder.add_edge("ejecutar", END)
    return builder.compile(checkpointer=MemorySaver())


def vacio(pedido: str, monto: float) -> dict:
    return {"pedido": pedido, "monto": monto, "aprobado": False, "resultado": ""}


def main() -> None:
    grafo = construir()

    chico = {"configurable": {"thread_id": "A1"}}
    grafo.invoke(vacio("A1", 500), chico)
    final_chico = grafo.get_state(chico)
    print("A1", "completado" if not final_chico.next else final_chico.next, final_chico.values["resultado"])

    grande = {"configurable": {"thread_id": "B2"}}
    grafo.invoke(vacio("B2", 2500), grande)
    pausado = grafo.get_state(grande)
    print("B2", "esperando_aprobacion" if pausado.next else "completado", pausado.next)

    grafo.invoke(Command(resume="no"), grande)
    print("B2", grafo.get_state(grande).values["resultado"])


if __name__ == "__main__":
    main()
