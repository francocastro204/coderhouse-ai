"""Ejercicio opcional de la unidad 2: una cadena LCEL asíncrona.

LCEL es el operador |. Cada pieza es un eslabón:

    prompt | modelo | parser

El prompt arma el mensaje, el modelo responde y el parser deja solo el texto.
ainvoke corre esa cadena con await, sin bloquear.

El modelo principal es Gemini. Hugging Face es el respaldo automático.
"""

import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from unidad_2.modelos import modelo_con_respaldo


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Respondé en español, en dos oraciones, con lenguaje simple.",
        ),
        ("human", "{pregunta}"),
    ]
)
model = modelo_con_respaldo()
parser = StrOutputParser()
chain = prompt | model | parser


async def main() -> None:
    respuesta = await chain.ainvoke({"pregunta": "¿Qué es LangChain?"})
    print(respuesta)


if __name__ == "__main__":
    asyncio.run(main())
