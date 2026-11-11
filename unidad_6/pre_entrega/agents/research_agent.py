"""Agente de investigación.

Consulta una base chica de políticas. Es el reemplazo local de Tavily
o de la vector DB de las pre-entregas 3 y 4: una función que busca
y devuelve el texto, sin decidir el caso.
"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

# Tres notas. La búsqueda mira palabras, no embeddings: así la demo
# corre sin Pinecone ni una clave de Tavily.
POLITICAS = [
    {
        "id": "devoluciones",
        "pistas": ["devolu", "reembol", "plazo", "tope", "devolver"],
        "texto": (
            "Política de devoluciones de Tienda Lumen: el cliente puede "
            "devolver hasta 10 días después de la compra, si el monto es "
            "de hasta 20000 pesos y el producto no tiene uso."
        ),
    },
    {
        "id": "envios",
        "pistas": ["envio", "envío", "flete", "despacho"],
        "texto": (
            "Política de envíos: el envío es gratis cuando la compra supera "
            "15000 pesos. Por debajo, el envío cuesta 2500 pesos."
        ),
    },
    {
        "id": "garantia",
        "pistas": ["garant", "falla", "fábrica", "fabrica"],
        "texto": (
            "Garantía: 90 días por falla de fábrica. No cubre golpes ni humedad."
        ),
    },
]

PROMPT = (
    "Sos el investigador de Tienda Lumen. "
    "Tu única herramienta es buscar_documentos. "
    "Buscá y copiá lo que dice la base, con los números. "
    "No digas si el reembolso corresponde. "
    "Si la herramienta no encuentra nada, respondé exactamente: No encontré una política."
)


class BusquedaInput(BaseModel):
    """La consulta que entra a la base de políticas."""

    consulta: str = Field(..., description="Tema a buscar, por ejemplo devoluciones")


@tool(args_schema=BusquedaInput)
def buscar_documentos(consulta: str) -> str:
    """Busca una política de Tienda Lumen. No calcula si un caso cumple."""
    texto = consulta.lower()
    mejor = None
    puntaje = 0
    for nota in POLITICAS:
        puntos = sum(1 for pista in nota["pistas"] if pista in texto)
        if puntos > puntaje:
            puntaje = puntos
            mejor = nota
    if mejor is None:
        return "No encontré una política para esa consulta."
    return mejor["texto"]


def crear_investigador(modelo):
    """ReAct acotado a buscar_documentos. No ve el historial del grafo."""
    return create_react_agent(
        modelo,
        [buscar_documentos],
        prompt=PROMPT,
        name="investigador",
    )
