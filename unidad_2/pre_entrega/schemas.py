"""Esquemas de la pre-entrega 2.

Pydantic describe la forma de la respuesta. El modelo no devuelve texto
libre: devuelve un objeto con estos campos.
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class NivelCriticidad(str, Enum):
    """Qué tan grave es lo que describe el texto."""

    baja = "baja"
    media = "media"
    alta = "alta"


class EntidadesTecnicas(BaseModel):
    """Lo que la cadena tiene que extraer de un texto técnico."""

    tecnologias: List[str] = Field(
        min_length=1,
        description="Tecnologías nombradas en el texto. Al menos una.",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="baja, media o alta, según el impacto si algo falla.",
    )
    resumen_tecnico: str = Field(
        description="Resumen corto, en español, de lo que hace el sistema.",
    )
