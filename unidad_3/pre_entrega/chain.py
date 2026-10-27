"""Cadena RAG de la pre-entrega 3.

Busca los fragmentos cercanos a la pregunta y le pide a Gemini que
responda solo con eso. Si el contexto no alcanza, la respuesta es
«No lo sé».
"""

import asyncio
import logging
from operator import itemgetter

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from unidad_2.modelos import modelo_gemini
from unidad_3.pre_entrega.schemas import RespuestaRAG
from unidad_3.pre_entrega.store import TOP_K, ingestar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logger = logging.getLogger("unidad_3.pre_entrega.chain")

parser = PydanticOutputParser(pydantic_object=RespuestaRAG)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sos un asistente técnico de AndesPay. Respondé solo con el "
            "CONTEXTO. Si la respuesta no está ahí, el campo respuesta debe "
            "ser exactamente «No lo sé» y referencias debe ser una lista vacía. "
            "No completes con conocimiento propio.\n{format_instructions}",
        ),
        ("human", "CONTEXTO:\n{contexto}\n\nPREGUNTA:\n{pregunta}"),
    ]
).partial(format_instructions=parser.get_format_instructions())


def _texto(documentos) -> str:
    return "\n\n".join(
        f"Fuente: {doc.metadata.get('fuente', 'desconocida')}\n{doc.page_content}"
        for doc in documentos
    )


def construir():
    """Arma la cadena. Indexa solo si Chroma todavía está vacío."""
    base = ingestar()
    retriever = base.as_retriever(search_kwargs={"k": TOP_K})
    return (
        {
            "contexto": itemgetter("pregunta") | retriever | RunnableLambda(_texto),
            "pregunta": itemgetter("pregunta"),
        }
        | prompt
        | modelo_gemini()
        | parser
    )


cadena = None


async def get_rag_response(query: str) -> RespuestaRAG:
    """Busca, arma el prompt, llama al modelo y valida la respuesta."""
    global cadena
    if cadena is None:
        cadena = construir()
    logger.info("Pregunta: %s", query)
    resultado = await cadena.ainvoke({"pregunta": query})
    logger.info(
        "Respuesta=%s referencias=%s",
        resultado.respuesta,
        resultado.referencias,
    )
    return resultado


async def main() -> None:
    dentro = await get_rag_response("¿Qué pasa si Redis deja de responder?")
    print("Pregunta cubierta por los documentos:")
    print(dentro.model_dump_json(indent=2, ensure_ascii=False))

    fuera = await get_rag_response("¿Cuánto cuesta el plan enterprise de AndesPay?")
    print("\nPregunta trampa:")
    print(fuera.model_dump_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
