"""Manda el orquestador de la unidad 6 a Phoenix.

Phoenix tiene que estar corriendo en el puerto 6006. La búsqueda
pasa por Chroma, así la traza muestra la base y no solo al modelo.
La última consulta corta la base a propósito.

Desde la raíz, con el entorno activo y Phoenix ya levantado:

    python unidad_7/7.1/instrumentar.py
"""

import asyncio
import json
import os
import sys
import warnings
from pathlib import Path

import urllib.request

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

os.environ.setdefault("PHOENIX_WORKING_DIR", str(CARPETA / "phoenix_data"))

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from phoenix.otel import register

from unidad_3.pre_entrega.store import embeddings
from unidad_6.pre_entrega.agents.research_agent import POLITICAS, buscar_documentos
from unidad_6.pre_entrega.graph import construir

warnings.filterwarnings(
    "ignore",
    message="coroutine 'ClientResponse.json' was never awaited",
    category=RuntimeWarning,
)
warnings.filterwarnings("ignore", message="create_react_agent has been moved")

PHOENIX = "http://127.0.0.1:6006"
PROYECTO = "tienda-lumen"
VECTORSTORE = CARPETA / "vectorstore"
HALLAZGOS = CARPETA / "hallazgos.json"
TRAZADOR = trace.get_tracer("tienda.chroma")
CORTAR_BASE = {"activo": False}

CONSULTAS = [
    "Un cliente quiere devolver un producto de 14500 pesos a los 12 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 8000 pesos a los 3 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 25000 pesos a los 5 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 18000 pesos a los 10 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
    "Un cliente quiere devolver un producto de 5000 pesos a los 15 días. Busca la política de devoluciones y decide si corresponde el reembolso.",
]


def phoenix_esta() -> bool:
    try:
        with urllib.request.urlopen(PHOENIX, timeout=3) as respuesta:
            return respuesta.status < 500
    except Exception:
        return False


def preparar_chroma():
    """Indexa las tres políticas una sola vez. La carpeta no se sube a git."""
    VECTORSTORE.mkdir(parents=True, exist_ok=True)
    store = Chroma(
        collection_name="politicas-lumen",
        embedding_function=embeddings(),
        persist_directory=str(VECTORSTORE),
    )
    if not store.get()["ids"]:
        store.add_documents(
            [
                Document(page_content=nota["texto"], metadata={"id": nota["id"]})
                for nota in POLITICAS
            ]
        )
    return store.as_retriever(search_kwargs={"k": 1})


def conectar_busqueda(retriever) -> None:
    """La herramienta del investigador busca en Chroma y deja un span propio."""
    respaldo = buscar_documentos.func

    def buscar_con_chroma(consulta: str) -> str:
        with TRAZADOR.start_as_current_span("chroma.buscar_politica") as span:
            span.set_attribute("openinference.span.kind", "RETRIEVER")
            span.set_attribute("input.value", consulta)
            if CORTAR_BASE["activo"]:
                span.set_status(Status(StatusCode.ERROR, "Base no disponible"))
                raise RuntimeError("Base de políticas no disponible")
            try:
                docs = retriever.invoke(consulta)
            except Exception as error:
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise
            if not docs:
                texto = respaldo(consulta)
            else:
                texto = docs[0].page_content
            span.set_attribute("output.value", texto)
            return texto

    buscar_documentos.func = buscar_con_chroma


def usar_modelo_estable() -> None:
    """Solo el modelo que responde. El otro se queda colgado y la traza no cierra."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    import unidad_6.pre_entrega.graph as grafo
    from unidad_2.modelos import modelo_gemini

    clave = modelo_gemini().google_api_key

    def modelo_fijo():
        return ChatGoogleGenerativeAI(
            model="gemini-flash-lite-latest",
            google_api_key=clave,
            temperature=0,
            max_retries=0,
            request_timeout=45,
        )

    grafo.modelo_orquestador = modelo_fijo


def instrumentar():
    proveedor = register(project_name=PROYECTO, endpoint=f"{PHOENIX}/v1/traces")
    LangChainInstrumentor().instrument(tracer_provider=proveedor)
    GoogleGenAIInstrumentor().instrument(tracer_provider=proveedor)
    return proveedor


async def correr_con_tope(app, pregunta: str) -> str:
    """Si Gemini no contesta, se corta a los 60 segundos y se intenta una vez más."""
    ultimo = None
    for intento in (1, 2):
        try:
            return await asyncio.wait_for(una(app, pregunta), timeout=60)
        except TimeoutError as error:
            ultimo = error
            print(f"  intento {intento} tardó más de 60s", flush=True)
    raise TimeoutError("Gemini no contestó a tiempo") from ultimo


async def una(app, pregunta: str) -> str:
    resultado = await app.ainvoke(
        {
            "messages": [HumanMessage(content=pregunta)],
            "aportes": [],
            "ruta": [],
            "pasos": 0,
            "next_agent": "",
            "task_completed": False,
            "instruccion": "",
        },
        {"recursion_limit": 20},
    )
    ultimo = resultado["messages"][-1]
    contenido = getattr(ultimo, "content", "")
    if isinstance(contenido, list):
        contenido = "".join(
            bloque.get("text", "") if isinstance(bloque, dict) else str(bloque)
            for bloque in contenido
        )
    return str(contenido).strip()


async def main() -> None:
    if not phoenix_esta():
        raise SystemExit("Phoenix no está en http://127.0.0.1:6006. Levantalo antes de este script.")
    proveedor = instrumentar()
    usar_modelo_estable()
    print("modelo: gemini-flash-lite-latest", flush=True)
    conectar_busqueda(preparar_chroma())
    app = construir()
    desde = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if HALLAZGOS.exists() and desde > 1:
        corridas = json.loads(HALLAZGOS.read_text(encoding="utf-8"))
        corridas = [item for item in corridas if not isinstance(item["n"], int) or item["n"] < desde]
        corridas = [item for item in corridas if item["n"] != "fallo"]
        print("espero 45s para que se libere el cupo de Gemini", flush=True)
        await asyncio.sleep(45)
    else:
        corridas = []
    for numero, pregunta in enumerate(CONSULTAS, start=1):
        if numero < desde:
            continue
        if numero > desde:
            await asyncio.sleep(25)
        print(f"\n=== Consulta {numero} ===", flush=True)
        try:
            respuesta = await correr_con_tope(app, pregunta)
            print(respuesta, flush=True)
            corridas.append({"n": numero, "ok": True, "pregunta": pregunta, "respuesta": respuesta})
        except Exception as error:
            print(f"error: {error}", flush=True)
            corridas.append({"n": numero, "ok": False, "pregunta": pregunta, "error": str(error)})
    print("\nespero 40s y corto la base a propósito", flush=True)
    await asyncio.sleep(40)
    print("\n=== Fallo a propósito ===", flush=True)
    CORTAR_BASE["activo"] = True
    try:
        respuesta = await correr_con_tope(app, CONSULTAS[0])
        print(respuesta, flush=True)
        corridas.append({"n": "fallo", "ok": True, "pregunta": CONSULTAS[0], "respuesta": respuesta})
    except Exception as error:
        print(f"error esperado: {error}", flush=True)
        corridas.append({"n": "fallo", "ok": False, "pregunta": CONSULTAS[0], "error": str(error)})
    proveedor.force_flush()
    HALLAZGOS.write_text(json.dumps(corridas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo. Respuestas en {HALLAZGOS.name}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
