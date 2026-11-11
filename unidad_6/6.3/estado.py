"""Dos agentes comparten el estado sin pisarse.

El investigador escribe solo researcher_output. El revisor escribe
solo reviewer_output. No hay una lista global ni un append.

Desde la raíz del repo:

    python unidad_6/6.3/estado.py
"""

import asyncio
from typing import List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field, ValidationError


class ResearchArtifact(BaseModel):
    """Lo que el investigador deja. El score no puede salir de 0 a 1."""

    topic: str
    findings: List[str]
    confidence_score: float = Field(ge=0, le=1)


class ReviewArtifact(BaseModel):
    """Lo que el revisor deja. No reescribe los hallazgos."""

    is_approved: bool
    feedback: str


class AgentState(TypedDict):
    topic: str
    researcher_output: Optional[ResearchArtifact]
    reviewer_output: Optional[ReviewArtifact]


async def researcher_node(state: AgentState) -> dict:
    print(f"--- Investigando: {state['topic']} ---")
    await asyncio.sleep(1)
    artefacto = ResearchArtifact(
        topic=state["topic"],
        findings=["Un supervisor reparte. Cada agente escribe solo su parte."],
        confidence_score=0.9,
    )
    return {"researcher_output": artefacto}


async def reviewer_node(state: AgentState) -> dict:
    print("--- Revisando resultados ---")
    dato = state.get("researcher_output")
    if dato is None:
        revision = ReviewArtifact(is_approved=False, feedback="No hay datos del investigador.")
    elif dato.confidence_score > 0.8:
        revision = ReviewArtifact(is_approved=True, feedback="El hallazgo es suficiente.")
    else:
        revision = ReviewArtifact(
            is_approved=False,
            feedback="La confianza es baja. Hay que investigar de nuevo.",
        )
    return {"reviewer_output": revision}


def construir():
    workflow = StateGraph(AgentState)
    workflow.add_node("investigador", researcher_node)
    workflow.add_node("revisor", reviewer_node)
    workflow.set_entry_point("investigador")
    workflow.add_edge("investigador", "revisor")
    workflow.add_edge("revisor", END)
    return workflow.compile()


def probar_score_invalido() -> None:
    """1.5 no entra en el contrato. El error se atrapa: el programa sigue."""
    print("--- Probando score 1.5 ---")
    try:
        ResearchArtifact(
            topic="Sistemas Multi-Agente",
            findings=["dato"],
            confidence_score=1.5,
        )
    except ValidationError as error:
        print(f"ValidationError manejado: {error.error_count()} error. El score queda fuera de 0 a 1.")


async def run_example() -> None:
    app = construir()
    inicial = {
        "topic": "Sistemas Multi-Agente",
        "researcher_output": None,
        "reviewer_output": None,
    }
    async for evento in app.astream(inicial):
        nodo, cambio = next(iter(evento.items()))
        print(f"Nodo '{nodo}' finalizado.")
        if nodo == "revisor":
            revision = cambio["reviewer_output"]
            print(f"Aprobado: {revision.is_approved}. {revision.feedback}")
    probar_score_invalido()


if __name__ == "__main__":
    asyncio.run(run_example())
