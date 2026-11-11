"""Agente de análisis.

Solo compara números. El plazo y el tope tienen que venir del
investigador. Si no están, no los inventa.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

PROMPT = (
    "Sos el analista de Tienda Lumen. No busques políticas. "
    "Tu única herramienta es validar_reembolso. "
    "Sacá los días y el monto de la pregunta del usuario. "
    "Sacá plazo_dias y tope del texto del investigador. "
    "Si falta un número, no inventes: respondé exactamente Faltan números. "
    "Cuando la herramienta responda, repetí su frase sin cambiar el veredicto."
)


class ValidacionInput(BaseModel):
    """Los cuatro números que la herramienta compara. Ninguno se busca acá."""

    dias: int = Field(..., description="Días desde la compra, según la pregunta")
    monto: int = Field(..., description="Monto del producto, según la pregunta")
    plazo_dias: int = Field(..., description="Días que permite la política")
    tope: int = Field(..., description="Monto máximo que permite la política")


@tool(args_schema=ValidacionInput)
def validar_reembolso(dias: int, monto: int, plazo_dias: int, tope: int) -> str:
    """Compara el caso con el plazo y el tope. No busca la política."""
    motivos: list[str] = []
    if dias > plazo_dias:
        motivos.append(f"pasó el plazo: van {dias} días y el límite es {plazo_dias}")
    if monto > tope:
        motivos.append(f"el monto {monto} supera el tope {tope}")
    if not motivos:
        return (
            f"Corresponde. {dias} días está dentro de {plazo_dias} "
            f"y {monto} está dentro del tope {tope}."
        )
    monto_ok = "entra en el tope" if monto <= tope else "además se pasa del tope"
    return f"No corresponde. {' '.join(motivos)}. El monto {monto} {monto_ok} de {tope}."


def crear_analista(modelo):
    """ReAct acotado a validar_reembolso. No ve el historial del grafo."""
    return create_react_agent(
        modelo,
        [validar_reembolso],
        prompt=PROMPT,
        name="analista",
    )
