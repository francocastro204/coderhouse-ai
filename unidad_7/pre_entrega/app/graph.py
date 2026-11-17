"""Arma el orquestador de la unidad 6 con Redis y la pausa humana.

El modelo es el que responde. gemini-3.1-flash-lite se queda colgado
cuando Google devuelve 503, y la traza no cierra.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from unidad_2.modelos import modelo_gemini
from unidad_6.pre_entrega import graph as grafo_unidad_6
from unidad_6.pre_entrega.graph import construir


def usar_modelo_estable() -> None:
    clave = modelo_gemini().google_api_key

    def modelo_fijo():
        return ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            google_api_key=clave,
            temperature=0,
            max_retries=0,
            request_timeout=45,
        )

    grafo_unidad_6.modelo_orquestador = modelo_fijo


def armar(checkpointer):
    usar_modelo_estable()
    return construir(checkpointer=checkpointer, con_aprobacion=True)
