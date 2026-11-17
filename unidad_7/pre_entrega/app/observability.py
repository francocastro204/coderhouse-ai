"""Manda cada corrida del grafo a Phoenix local.

Phoenix tiene que estar en el puerto 6006. Si no está, la API igual
responde: las trazas se pierden, el job no.
"""

import os

from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

PROYECTO = os.getenv("PHOENIX_PROJECT", "pre-entrega-7")
ENDPOINT = os.getenv("PHOENIX_ENDPOINT", "http://127.0.0.1:6006/v1/traces")


def iniciar():
    proveedor = register(project_name=PROYECTO, endpoint=ENDPOINT)
    LangChainInstrumentor().instrument(tracer_provider=proveedor)
    GoogleGenAIInstrumentor().instrument(tracer_provider=proveedor)
    print(f"Trazas hacia {ENDPOINT} proyecto {PROYECTO}", flush=True)
    return proveedor
