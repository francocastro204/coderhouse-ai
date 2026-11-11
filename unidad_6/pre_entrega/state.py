"""Estado compartido del orquestador.

MessagesState ya trae `messages`, con el reductor que anexa mensajes.
Los campos de abajo son los que esta entrega agrega para no perder
quién aportó qué cuando los agentes se turnan.
"""

import operator
from typing import Annotated

from langgraph.graph import MessagesState
from typing_extensions import TypedDict


class Aporte(TypedDict):
    """Lo que un especialista dejó por escrito. No pisa el aporte del otro."""

    agente: str
    texto: str
    herramientas: list[str]


class EstadoOrquestador(MessagesState):
    """Lo que ven el supervisor y los nodos del grafo.

    `next_agent` es la decisión de ruteo: investigador, analista,
    finalizar o sintesis.
    `task_completed` pasa a True solo cuando la validación acepta cerrar.
    `instruccion` es la frase para el próximo especialista, no el historial entero.
    `pasos` cuenta visitas al supervisor. Es el freno del bucle.
    `aportes` y `ruta` se acumulan: cada nodo suma el suyo.
    """

    next_agent: str
    task_completed: bool
    instruccion: str
    pasos: int
    aportes: Annotated[list[Aporte], operator.add]
    ruta: Annotated[list[str], operator.add]
