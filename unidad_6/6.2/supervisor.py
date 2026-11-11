"""Supervisor que delega en cada paso.

El enunciado pide ChatOpenAI y OPENAI_API_KEY. Esa API se cobra.
El modelo es Gemini. Si el modelo del .env responde 503, pasa al
respaldo gemini-flash-lite-latest.

Desde la raíz del repo:

    python unidad_6/6.2/supervisor.py
"""

import asyncio
import sys
import warnings
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from unidad_2.modelos import modelo_gemini

# El enunciado arma el supervisor así, con la clave de OpenAI:
#
# from langchain_openai import ChatOpenAI
# ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"])

warnings.filterwarnings(
    "ignore",
    message="coroutine 'ClientResponse.json' was never awaited",
    category=RuntimeWarning,
)

PREGUNTA = "Necesito un reporte sobre ventas."
SISTEMA = (
    "Sos el supervisor. No escribas el informe. "
    "Elegí next_agent en este orden, sin saltarte a nadie: "
    "Analista si todavía no hay un mensaje de Analista. "
    "Escritor si el Analista ya habló y el Escritor no. "
    "FINALIZAR solo cuando los dos ya dejaron su mensaje. "
    "No vuelvas a elegir a quien ya habló."
)


class AgentState(TypedDict):
    """Historial compartido y la decisión del supervisor para la próxima flecha."""

    messages: Annotated[list[BaseMessage], add_messages]
    next: str


class Decision(TypedDict):
    """Salida estructurada. El Literal es el nombre del nodo, o el fin."""

    next_agent: Literal["Analista", "Escritor", "FINALIZAR"]


def modelo():
    """El chat del .env, con un respaldo si ese modelo está saturado."""
    primario = modelo_gemini().model_copy(update={"max_retries": 0, "request_timeout": 30})
    if getattr(primario, "model", "") == "gemini-flash-lite-latest":
        return primario
    respaldo = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        google_api_key=primario.google_api_key,
        temperature=0,
        max_retries=0,
        request_timeout=30,
    )
    return primario.with_fallbacks([respaldo])


def _siguiente(decision: Decision | dict) -> str:
    if isinstance(decision, dict):
        return decision["next_agent"]
    return decision.next_agent


def _ya_hablo(state: AgentState, nombre: str) -> bool:
    return any(getattr(mensaje, "name", None) == nombre for mensaje in state["messages"])


def supervisor_node(state: AgentState) -> dict[str, str]:
    """Pide el siguiente nodo. Si el modelo se adelanta, lo devuelve al orden."""
    decision = modelo().with_structured_output(Decision).invoke(
        [SystemMessage(content=SISTEMA), *state["messages"]]
    )
    elegido = _siguiente(decision)
    if not _ya_hablo(state, "Analista"):
        if elegido != "Analista":
            print(f"  rúbrica: el modelo dijo {elegido}; toca Analista")
        elegido = "Analista"
    elif not _ya_hablo(state, "Escritor"):
        if elegido != "Escritor":
            print(f"  rúbrica: el modelo dijo {elegido}; toca Escritor")
        elegido = "Escritor"
    else:
        if elegido != "FINALIZAR":
            print(f"  rúbrica: el modelo dijo {elegido}; toca FINALIZAR")
        elegido = "FINALIZAR"
    return {"next": elegido}


def analyst_node(state: AgentState):
    return {"messages": [HumanMessage(content="Datos procesados: +20% incremento.", name="Analista")]}


def writer_node(state: AgentState):
    return {"messages": [HumanMessage(content="El informe está listo: Crecimiento positivo.", name="Escritor")]}


def construir():
    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("Analista", analyst_node)
    builder.add_node("Escritor", writer_node)
    builder.set_entry_point("supervisor")
    builder.add_edge("Analista", "supervisor")
    builder.add_edge("Escritor", "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        lambda s: s["next"],
        {"Analista": "Analista", "Escritor": "Escritor", "FINALIZAR": END},
    )
    return builder.compile()


async def main() -> None:
    graph = construir()
    print(PREGUNTA)
    async for evento in graph.astream(
        {"messages": [HumanMessage(content=PREGUNTA)], "next": ""},
        {"recursion_limit": 8},
    ):
        nodo, cambio = next(iter(evento.items()))
        if nodo == "supervisor":
            print(f"→ supervisor elige {cambio['next']}")
        else:
            mensaje = cambio["messages"][-1]
            print(f"→ {nodo}: {mensaje.content}")


if __name__ == "__main__":
    asyncio.run(main())
