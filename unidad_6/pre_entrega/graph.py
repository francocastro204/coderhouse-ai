"""Grafo jerárquico.

El supervisor elige el siguiente nodo. Los especialistas no se hablan:
vuelven al supervisor con un aporte corto. Validar no deja cerrar si
falta la búsqueda o el cálculo. El tope de pasos corta el bucle.
"""

import warnings
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from unidad_2.modelos import modelo_gemini

# El enunciado pide create_react_agent. LangGraph 1.0 avisa que se mudó
# a langchain.agents. El aviso no cambia el grafo.
warnings.filterwarnings("ignore", message="create_react_agent has been moved")
warnings.filterwarnings(
    "ignore",
    message="coroutine 'ClientResponse.json' was never awaited",
    category=RuntimeWarning,
)
from unidad_6.pre_entrega.agents.analyst_agent import crear_analista
from unidad_6.pre_entrega.agents.research_agent import crear_investigador
from unidad_6.pre_entrega.state import EstadoOrquestador

MAX_PASOS = 6
MAX_POR_AGENTE = 2

PROMPT_SUPERVISOR = (
    "Sos el supervisor de Tienda Lumen. No respondas al cliente y no calcules. "
    "Elegí un solo siguiente: "
    "investigador si falta la política, "
    "analista si ya está la política y falta el veredicto, "
    "finalizar solo si los dos ya usaron su herramienta. "
    "La instruccion es una frase para ese especialista. "
    "Si elegís finalizar, dejá la instruccion vacía."
)

PROMPT_SINTESIS = (
    "Escribí la respuesta final en español, en máximo 4 líneas. "
    "Usá solo los aportes. El veredicto es el del analista. "
    "La política es la del investigador. Si un aporte falta, decilo. "
    "No inventes otros plazos ni otros montos."
)


class DecisionSupervisor(BaseModel):
    """Lo que el supervisor devuelve. Literal mapea a los nodos del grafo."""

    siguiente: Literal["investigador", "analista", "finalizar"]
    instruccion: str = Field(
        default="",
        description="Qué debe hacer el especialista. Vacío si el siguiente es finalizar.",
    )


def texto_de(mensaje: Any) -> str:
    contenido = getattr(mensaje, "content", mensaje)
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


def pregunta_de(state: EstadoOrquestador) -> str:
    for mensaje in state.get("messages") or []:
        if getattr(mensaje, "type", "") == "human":
            return texto_de(mensaje)
    return ""


def faltante(state: EstadoOrquestador) -> str | None:
    """Quién falta para poder cerrar.

    El análisis solo cuenta si llegó después de una búsqueda con herramienta.
    Si el analista corre antes y adivina números, hay que pedirle el cálculo de nuevo.
    None cuando la búsqueda y el cálculo posterior ya están, o cuando ese
    especialista ya agotó sus dos turnos.
    """
    investigo = False
    analizo_despues = False
    usos_investigador = 0
    usos_analista = 0
    for aporte in state.get("aportes") or []:
        if aporte["agente"] == "investigador":
            usos_investigador += 1
            if "buscar_documentos" in aporte["herramientas"]:
                investigo = True
        elif aporte["agente"] == "analista":
            usos_analista += 1
            if investigo and "validar_reembolso" in aporte["herramientas"]:
                analizo_despues = True
    if not investigo and usos_investigador < MAX_POR_AGENTE:
        return "investigador"
    if not analizo_despues and usos_analista < MAX_POR_AGENTE:
        return "analista"
    return None


def instruccion_por_defecto(agente: str) -> str:
    if agente == "analista":
        return (
            "Tomá el plazo y el tope del investigador, y los días y el monto "
            "de la pregunta. Llamá a validar_reembolso."
        )
    return "Buscá en la base la política que aplica a la pregunta. No decidas el caso."


def resumen_aportes(state: EstadoOrquestador) -> str:
    aportes = state.get("aportes") or []
    if not aportes:
        return "Todavía no hay aportes."
    lineas = []
    for aporte in aportes:
        herramientas = ", ".join(aporte["herramientas"]) or "ninguna"
        lineas.append(f"- {aporte['agente']} ({herramientas}): {aporte['texto']}")
    return "\n".join(lineas)


def llamadas_de(mensajes: list[Any]) -> list[str]:
    nombres = []
    for mensaje in mensajes:
        for llamada in getattr(mensaje, "tool_calls", None) or []:
            nombre = llamada.get("name")
            if nombre:
                nombres.append(nombre)
    return nombres


def modelo_orquestador():
    """Gemini con tope de espera.

    gemini-3.1-flash-lite a veces responde 503 por demanda. En ese caso
    la misma llamada pasa a gemini-flash-lite-latest. max_retries=0 evita
    que el cliente se quede reintentando en silencio.
    """
    primario = modelo_gemini().model_copy(update={"max_retries": 0, "request_timeout": 30})
    if getattr(primario, "model", "") == "gemini-flash-lite-latest":
        return primario
    respaldo = ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        google_api_key=primario.google_api_key,
        temperature=0.2,
        max_retries=0,
        request_timeout=30,
    )
    return primario.with_fallbacks([respaldo])


def construir():
    """Arma el grafo. Los ReAct viven dentro del nodo, no como historial común."""
    investigador = crear_investigador(modelo_orquestador())
    analista = crear_analista(modelo_orquestador())
    supervisor_modelo = modelo_orquestador().with_structured_output(DecisionSupervisor)
    sintesis_modelo = modelo_orquestador()

    async def nodo_supervisor(state: EstadoOrquestador) -> dict[str, Any]:
        pasos = state.get("pasos", 0) + 1
        if pasos > MAX_PASOS:
            print(f"→ supervisor: finalizar (tope de {MAX_PASOS} pasos)")
            return _cierre(state, pasos)

        instruccion = ""
        try:
            decision = await supervisor_modelo.ainvoke(
                [
                    SystemMessage(content=PROMPT_SUPERVISOR),
                    HumanMessage(
                        content=(
                            f"Pregunta:\n{pregunta_de(state)}\n\n"
                            f"Aportes:\n{resumen_aportes(state)}"
                        )
                    ),
                ]
            )
            elegido = decision.siguiente
            instruccion = (decision.instruccion or "").strip()
            origen = "modelo"
        except Exception as error:
            elegido = faltante(state) or "finalizar"
            origen = f"respaldo ({error.__class__.__name__})"

        # La rúbrica corrige al modelo: no se cierra si falta un especialista,
        # y nadie entra una tercera vez.
        falta = faltante(state)
        if falta is None:
            if elegido != "finalizar":
                origen = f"rúbrica, ya están los dos aportes; el modelo quería {elegido}"
            elegido = "finalizar"
        elif elegido != falta:
            origen = f"rúbrica, el modelo quería {elegido}; toca {falta}"
            elegido = falta
            instruccion = instruccion_por_defecto(falta)
        elif _usos(state, elegido) >= MAX_POR_AGENTE:
            origen = f"rúbrica, {elegido} ya intervino {MAX_POR_AGENTE} veces"
            elegido = falta if _usos(state, falta) < MAX_POR_AGENTE else "finalizar"

        if elegido == "finalizar":
            print(f"→ supervisor: finalizar ({origen})")
            return _cierre(state, pasos)

        if not instruccion:
            instruccion = instruccion_por_defecto(elegido)
        print(f"→ supervisor: {elegido} ({origen})")
        return {
            "pasos": pasos,
            "next_agent": elegido,
            "task_completed": False,
            "instruccion": instruccion,
            "ruta": ["supervisor"],
            "messages": [
                AIMessage(
                    content=f"Supervisor envía a {elegido}: {instruccion}",
                    name="supervisor",
                )
            ],
        }

    def _cierre(state: EstadoOrquestador, pasos: int) -> dict[str, Any]:
        return {
            "pasos": pasos,
            "next_agent": "finalizar",
            "task_completed": faltante(state) is None,
            "instruccion": "",
            "ruta": ["supervisor"],
            "messages": [
                AIMessage(content="Supervisor envía a validar.", name="supervisor")
            ],
        }

    async def nodo_investigador(state: EstadoOrquestador) -> dict[str, Any]:
        instruccion = state.get("instruccion") or instruccion_por_defecto("investigador")
        print(f"  investigador: {instruccion}")
        return await _correr_especialista(
            investigador,
            "investigador",
            (
                f"Pregunta del usuario:\n{pregunta_de(state)}\n\n"
                f"Tu tarea:\n{instruccion}"
            ),
        )

    async def nodo_analista(state: EstadoOrquestador) -> dict[str, Any]:
        instruccion = state.get("instruccion") or instruccion_por_defecto("analista")
        dato = "Todavía no hay dato del investigador."
        for aporte in reversed(state.get("aportes") or []):
            if aporte["agente"] == "investigador":
                dato = aporte["texto"]
                break
        print(f"  analista: {instruccion}")
        return await _correr_especialista(
            analista,
            "analista",
            (
                f"Pregunta del usuario:\n{pregunta_de(state)}\n\n"
                f"Dato del investigador:\n{dato}\n\n"
                f"Tu tarea:\n{instruccion}"
            ),
        )

    def nodo_validar(state: EstadoOrquestador) -> dict[str, Any]:
        # La rúbrica vive acá, no solo en el prompt: sin las dos herramientas no hay END.
        falta = faltante(state)
        if state.get("pasos", 0) > MAX_PASOS:
            falta = None
        if falta:
            instruccion = instruccion_por_defecto(falta)
            print(f"→ validar: falta {falta}, vuelve a ese especialista")
            return {
                "next_agent": falta,
                "task_completed": False,
                "instruccion": instruccion,
                "ruta": ["validar"],
                "messages": [
                    AIMessage(
                        content=f"Validación: falta {falta}. {instruccion}",
                        name="validar",
                    )
                ],
            }
        print("→ validar: los dos aportes están, pasa a síntesis")
        return {
            "next_agent": "sintesis",
            "task_completed": True,
            "ruta": ["validar"],
            "messages": [
                AIMessage(
                    content="Validación: hay búsqueda y análisis. Se puede cerrar.",
                    name="validar",
                )
            ],
        }

    async def nodo_sintesis(state: EstadoOrquestador) -> dict[str, Any]:
        try:
            respuesta = await sintesis_modelo.ainvoke(
                [
                    SystemMessage(content=PROMPT_SINTESIS),
                    HumanMessage(
                        content=(
                            f"Pregunta:\n{pregunta_de(state)}\n\n"
                            f"Aportes:\n{resumen_aportes(state)}"
                        )
                    ),
                ]
            )
            texto = texto_de(respuesta).strip()
        except Exception as error:
            texto = f"No pude redactar la síntesis ({error.__class__.__name__}).\n{resumen_aportes(state)}"
        print("→ síntesis")
        return {
            "ruta": ["sintesis"],
            "messages": [AIMessage(content=texto, name="sintesis")],
        }

    workflow = StateGraph(EstadoOrquestador)
    workflow.add_node("supervisor", nodo_supervisor)
    workflow.add_node("investigador", nodo_investigador)
    workflow.add_node("analista", nodo_analista)
    workflow.add_node("validar", nodo_validar)
    workflow.add_node("sintesis", nodo_sintesis)
    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        ruta_supervisor,
        {
            "investigador": "investigador",
            "analista": "analista",
            "validar": "validar",
        },
    )
    workflow.add_edge("investigador", "supervisor")
    workflow.add_edge("analista", "supervisor")
    workflow.add_conditional_edges(
        "validar",
        ruta_validar,
        {
            "investigador": "investigador",
            "analista": "analista",
            "sintesis": "sintesis",
        },
    )
    workflow.add_edge("sintesis", END)
    return workflow.compile()


def _usos(state: EstadoOrquestador, agente: str) -> int:
    return sum(1 for aporte in state.get("aportes") or [] if aporte["agente"] == agente)


def ruta_supervisor(state: EstadoOrquestador) -> Literal["investigador", "analista", "validar"]:
    """El Literal del supervisor. `finalizar` no es un nodo: entra a validar."""
    elegido = state.get("next_agent")
    if elegido == "analista":
        return "analista"
    if elegido == "finalizar":
        return "validar"
    return "investigador"


def ruta_validar(state: EstadoOrquestador) -> Literal["investigador", "analista", "sintesis"]:
    elegido = state.get("next_agent")
    if elegido == "investigador":
        return "investigador"
    if elegido == "analista":
        return "analista"
    return "sintesis"


async def _correr_especialista(agente, nombre: str, contenido: str) -> dict[str, Any]:
    resultado = await agente.ainvoke(
        {"messages": [HumanMessage(content=contenido)]},
        {"recursion_limit": 8},
    )
    mensajes = resultado["messages"]
    herramientas = llamadas_de(mensajes)
    texto = texto_de(mensajes[-1]).strip()
    for nombre_tool in herramientas:
        print(f"  herramienta: {nombre_tool}")
    print(f"  aporte: {texto}")
    return {
        "aportes": [{"agente": nombre, "texto": texto, "herramientas": herramientas}],
        "ruta": [nombre],
        "messages": [AIMessage(content=texto, name=nombre)],
    }
