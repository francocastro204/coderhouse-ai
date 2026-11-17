"""Pausa el grafo si el reembolso saldría.

No es crítico cuando el analista dice que no corresponde: no sale plata.
Si dice que corresponde, interrupt guarda el hilo en Redis y espera
un si o un no. El efecto queda en la síntesis, después de la pausa.
"""

from typing import Any, Literal

from langchain_core.messages import AIMessage
from langgraph.types import interrupt


def es_critico(state: dict) -> bool:
    """Corresponde pagar. «No corresponde» no entra: no empieza con «corresponde»."""
    for aporte in reversed(state.get("aportes") or []):
        if aporte.get("agente") != "analista":
            continue
        texto = (aporte.get("texto") or "").strip().lower()
        return texto.startswith("corresponde")
    return False


def nodo_aprobacion(state: dict) -> dict[str, Any]:
    if not es_critico(state):
        print("→ aprobacion: no es crítico, sigue", flush=True)
        return {"aprobado": True, "ruta": ["aprobacion"]}

    from unidad_6.pre_entrega.graph import pregunta_de

    print("→ aprobacion: el reembolso saldría, se pausa", flush=True)
    decision = interrupt(
        {
            "pregunta": "El analista dice que corresponde el reembolso. ¿Lo aprobás?",
            "caso": pregunta_de(state),
        }
    )
    if decision == "si":
        print("→ aprobacion: la persona dijo que sí", flush=True)
        return {"aprobado": True, "ruta": ["aprobacion"]}
    print("→ aprobacion: la persona dijo que no", flush=True)
    return {
        "aprobado": False,
        "ruta": ["aprobacion"],
        "messages": [
            AIMessage(content="Reembolso rechazado por el revisor.", name="aprobacion")
        ],
    }


def ruta_aprobacion(state: dict) -> Literal["sintesis", "fin"]:
    if state.get("aprobado"):
        return "sintesis"
    return "fin"
