"""Pre-entrega 2: extraer entidades técnicas con una cadena LCEL.

La cadena pide un objeto EntidadesTecnicas, no un párrafo suelto.
Gemini es el principal. Si falla, Hugging Face intenta lo mismo.
with_retry reintenta hasta 3 veces antes de darse por vencido.

with_structured_output se aplica a cada modelo por separado. El respaldo
de LangChain no tiene ese método: hay que pedirlo antes de with_fallbacks.
"""

import asyncio
import logging

from langchain_core.prompts import ChatPromptTemplate

from unidad_2.modelos import modelo_gemini, modelo_huggingface
from unidad_2.pre_entrega.schemas import EntidadesTecnicas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("unidad_2.pre_entrega.chain")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extraé las tecnologías del texto, un nivel de criticidad "
            "(baja, media o alta) y un resumen técnico breve en español.",
        ),
        ("human", "{texto}"),
    ]
)

principal = modelo_gemini().with_structured_output(EntidadesTecnicas)
# json_schema: Hugging Face no arma Pydantic con function calling.
respaldo = modelo_huggingface().with_structured_output(
    EntidadesTecnicas,
    method="json_schema",
)
model = principal.with_fallbacks([respaldo]).with_retry(stop_after_attempt=3)
chain = prompt | model


async def process_text(text: str) -> EntidadesTecnicas:
    """Manda el texto por la cadena y devuelve el objeto validado."""
    logger.info("Procesando texto de %s caracteres", len(text))
    resultado = await chain.ainvoke({"texto": text})
    logger.info(
        "Listo. Tecnologías=%s criticidad=%s",
        resultado.tecnologias,
        resultado.nivel_de_criticidad.value,
    )
    return resultado


async def main() -> None:
    texto = (
        "El checkout está armado con FastAPI. Las sesiones viven en Redis "
        "y los pedidos se guardan en PostgreSQL. Si Redis se cae, nadie "
        "puede pagar."
    )
    resultado = await process_text(texto)
    print(resultado.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
