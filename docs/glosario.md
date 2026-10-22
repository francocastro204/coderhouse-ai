# Glosario

Este archivo es un diccionario. Sirve para consultar qué significa un término (LLM, temperatura, Pydantic, asyncio, LangChain, LangGraph y el resto) sin tener que buscarlo en medio del código. Cada entrada dice qué es y, cuando aplica, en qué archivo de este repo entra.

No se ejecuta. Si aparece una palabra nueva en clase, el lugar para definirla es este.

La sintaxis de Python está en [python-basico.md](python-basico.md). El mapa del programa está en [arquitectura.md](arquitectura.md).

## Índice

- [Modelos](#modelos)
- [La llamada al modelo](#la-llamada-al-modelo)
- [Formas de usar un LLM](#formas-de-usar-un-llm)
- [Python y librerías de este repo](#python-y-librerías-de-este-repo)
- [Frameworks que vas a escuchar en el curso](#frameworks-que-vas-a-escuchar-en-el-curso)
- [APIs, cuentas y errores](#apis-cuentas-y-errores)
- [Piezas de nuestro código](#piezas-de-nuestro-código)

---

## Modelos

### IA (inteligencia artificial)

Programas que resuelven tareas que asociamos con criterio humano: clasificar, traducir, responder, decidir. Es el paraguas. Un LLM es un tipo de IA.

### Machine learning

Forma de construir IA en la que el programa aprende patrones a partir de ejemplos, en vez de llevar todas las reglas escritas a mano.

### Modelo

El resultado de ese aprendizaje: un montón de números (pesos) más la receta para usarlos. “Llamar a un modelo” es pedirle que calcule una salida a partir de tu entrada. En este repo el modelo se elige con variables como `GEMINI_MODEL` o `OPENAI_MODEL`.

### LLM (Large Language Model)

Modelo de lenguaje grande. Está entrenado con muchísimo texto y aprende a predecir el token siguiente. Encadenando predicciones, escribe una respuesta. GPT, Claude, Gemini y los modelos de Hugging Face que vamos a llamar son LLMs.

No “sabe” ni “busca en internet” por sí mismo. Genera texto probable según el prompt y lo que vio en el entrenamiento. Por eso a veces inventa datos con seguridad. Eso se llama alucinación.

### Transformer

Arquitectura de red neuronal en la que se apoyan casi todos los LLMs actuales. Su pieza central es la atención: al generar una palabra, el modelo puede mirar distintas partes del texto de entrada y darles distinto peso.

### GPT

Familia de modelos de OpenAI (Generative Pre-trained Transformer). En la práctica vas a ver nombres concretos: `gpt-4o-mini`, `gpt-4o`, etc. El nombre del producto y el nombre del modelo no son lo mismo.

### Claude

Familia de modelos de Anthropic. El SDK se llama `anthropic`. Un nombre típico de modelo es `claude-3-5-haiku` o uno más nuevo de la misma línea.

### Gemini

Familia de modelos de Google. La clave gratis sale de [Google AI Studio](https://aistudio.google.com/apikey). El SDK actual es `google-genai`.

### Hugging Face

Sitio y empresa donde se publican modelos, datasets y demos. Una cuenta te da un token para llamar a la Inference API. Hugging Face es la plataforma. El modelo es otro dato, por ejemplo `meta-llama/Llama-3.1-8B-Instruct`. El plan gratis tiene un cupo chico.

### Inferencia

Usar un modelo ya entrenado para obtener una respuesta. Es lo que hace este cliente. Entrenar es otra etapa, mucho más cara, y no la hacemos acá.

### Entrenamiento

Proceso en el que el modelo ajusta sus pesos viendo ejemplos. Queda fuera de esta pre-entrega.

### Fine-tuning

Seguir entrenando un modelo ya hecho, con datos propios, para que se especialice. Tampoco es esta entrega: nosotros solo llamamos modelos ya publicados.

### Parámetros del modelo

Los pesos aprendidos. Son millones o miles de millones de números. No los editás vos. Se confunden fácil con los parámetros de la llamada (`temperature`, `max_tokens`), que sí configurás en cada pregunta.

### Token

Pedazo de texto con el que el modelo lee y escribe. Puede ser una palabra, un trozo de palabra o un signo. “entropía” puede ser uno o varios tokens. Las APIs cobran y limitan por tokens, no por palabras.

### Tokenizador

El componente que parte el texto en tokens y los vuelve a juntar. Cada familia de modelos tiene el suyo. Por eso la misma frase puede “costar” distinto en GPT y en Claude.

### Ventana de contexto (context window)

Cuánto texto entra en una sola llamada, sumando el prompt y la respuesta, medido en tokens. Si te pasás, la API rechaza el pedido o recorta. Modelos distintos tienen ventanas distintas.

### Alucinación

Respuesta inventada, dicha con tono seguro. El modelo completó un texto probable y ese texto no era cierto. Bajar la temperatura reduce la variedad. Verificar la respuesta es otra capa (no la de esta pre-entrega).

### Embedding

Lista de números que representa el significado de un texto. Sirve para buscar cosas parecidas (“esta pregunta se parece a este documento”). Un chat normal, como el de esta entrega, devuelve texto. Un embedding devuelve el vector.

### Multimodal

Modelo que acepta más de un tipo de entrada: texto, imagen, audio. Esta pre-entrega usa solo texto.

---

## La llamada al modelo

### Prompt

El texto que le mandás al modelo. En un chat no es un solo string suelto: es una lista de mensajes con rol.

### Rol

Quién dice cada mensaje.

| Rol | Quién es |
| --- | --- |
| `system` | Instrucciones fijas: “respondé breve, en español”. |
| `user` | La persona. |
| `assistant` | El modelo, en turnos anteriores. |
| `tool` | El resultado de una herramienta, cuando hay agentes. Acá todavía no. |

En el código eso va a ser un `ChatMessage`: `role` + `content`.

### System prompt

El mensaje de rol `system`. Fija el comportamiento de la conversación. No lo ve el usuario final como parte del chat, pero el modelo sí.

### Chat completion

Pedirle al modelo que continúe una conversación y devuelva el próximo mensaje del asistente. Es la operación de esta pre-entrega. “Completion” a secas, en APIs viejas, era completar un solo texto sin roles.

### Temperatura (`temperature`)

Número que controla qué tan azarosa es la elección del próximo token.

| Valor | Efecto |
| --- | --- |
| `0` | Casi siempre el token más probable. Respuestas estables. Útil para extraer datos. |
| alrededor de `0.7` | Un punto medio. Respuestas variadas y todavía coherentes. |
| cerca de `2` | Mucha variedad. Más creatividad y más riesgo de texto raro. |

El enunciado pide validar temperatura entre **0 y 2**, que es el rango de OpenAI. Anthropic usa **0 a 1**. Cuando implementemos los clientes, el esquema acepta 0–2 y cada proveedor traduce ese valor a lo que su API permite.

Temperatura y `top_p` mueven la misma perilla (el azar). En la práctica se ajusta una y la otra se deja en el default.

### `max_tokens`

Tope de tokens de la **respuesta**, sin contar el prompt. Si el tope es bajo, la respuesta se corta a la mitad. Si es alto, la llamada puede costar más y tardar más, aunque el modelo puede frenar antes.

### `top_p`

Otra forma de limitar el azar. El modelo se queda con el conjunto más chico de tokens cuya probabilidad suma `top_p` (por ejemplo `0.9`) y sortea dentro de ese conjunto. Se llama nucleus sampling. En esta entrega el campo que el enunciado exige es la temperatura.

### `stop`

Lista de textos que, si aparecen, cortan la generación. Opcional. Sirve cuando querés que el modelo no siga después de un separador.

### Streaming

La API envía la respuesta por partes, a medida que se genera, en vez de esperar el texto entero. En el código es un generador asíncrono: `yield` de cada fragmento. Quien lo consume hace `async for`.

El modo normal (`generate`) espera el `ModelResponse` completo. El modo streaming imprime cada pedazo al llegar. `unidad_1/pre_entrega/main.py` va a probar los dos con la pregunta “¿Qué es la entropía?”.

### Latencia

Cuánto tarda en volver la respuesta. El streaming mejora la latencia percibida: ves la primera palabra antes de que termine el párrafo. El tiempo total puede ser parecido.

### Structured output

Pedirle al modelo que la respuesta cumpla un esquema (por ejemplo un JSON con campos fijos), y validar ese JSON con Pydantic. Esta pre-entrega valida la **entrada** y la **respuesta de nuestro cliente**. Forzar el JSON del modelo es un paso posterior del curso.

### Tool calling (function calling)

El modelo, en vez de responder solo con texto, pide ejecutar una función de tu programa (“buscá el clima en Lima”) con argumentos. Tu código corre la función y le devuelve el resultado. Es la base de muchos agentes. Esta entrega todavía no lo implementa.

### JSON

Formato de texto para datos: objetos, listas, strings, números. Las APIs hablan JSON. Pydantic nos evita armar esos diccionarios a mano en el resto del programa.

---

## Formas de usar un LLM

### Zero-shot

Pedir una tarea sin darle ejemplos. “Clasificá este texto en positivo o negativo” y nada más.

### Few-shot

Incluir unos pocos ejemplos dentro del prompt para marcar el formato o el criterio. Sigue siendo una llamada normal. Cambia el texto, no el cliente.

### Chain of thought

Pedirle al modelo que razone paso a paso antes de la respuesta final. Se hace con el prompt (“pensá paso a paso”). No es una librería.

### RAG (Retrieval Augmented Generation)

Antes de llamar al modelo, buscar trozos de tus documentos relevantes y pegarlos en el prompt. Así la respuesta se apoya en ese material y no solo en la memoria del entrenamiento. Usa embeddings y, casi siempre, una base de vectores. No es esta entrega.

### Chunk

Trozo de un documento, cortado para poder buscarlo e insertarlo en el prompt. Un PDF entero no entra en la ventana de contexto.

### Base de vectores (vector database)

Base especializada en guardar embeddings y devolver los más parecidos a una consulta. Ejemplos que vas a escuchar: Chroma, Pinecone, pgvector, FAISS.

### Agente

Un programa en el que el modelo no responde una sola vez: observa, elige una herramienta, mira el resultado y decide el paso siguiente. Puede dar varias vueltas. LangGraph es una forma de construir eso.

### Evaluación (evals)

Medir, con ejemplos fijos, si las respuestas sirven: exactitud, formato, si se inventó datos. Sin evals, un cambio de prompt o de modelo se juzga a ojo.

### Guardrails

Controles alrededor del modelo: validar el formato, filtrar datos sensibles, rechazar pedidos, reintentar si la salida no cumple el esquema. Pydantic, en este repo, es un guardrail de la entrada.

---

## Python y librerías de este repo

### Python 3.12

Versión del lenguaje que pide el enunciado. Las features nuevas de esa versión no son el foco. Sí importa instalar esa rama y no una 3.9 vieja, porque los SDK y la sintaxis de tipos que vamos a usar asumen una versión reciente.

### Módulo

Un archivo `.py`. `schemas.py` es un módulo.

### Paquete

Una carpeta con `__init__.py` que agrupa módulos. `llm_client` es el paquete.

### Type hint

Anotación de tipo: `nombre: str`, `-> ModelResponse`. Documenta y ayuda al editor. Ver [python-basico.md](python-basico.md).

### Pydantic

Librería que define clases de datos y las valida al crearlas. Si falta un campo, el rol no es válido o la temperatura es `3`, Pydantic lanza un error claro antes de llamar a la API.

En la versión 2, las clases heredan de `BaseModel` y los límites se declaran con `Field`.

```python
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    temperature: float = Field(ge=0, le=2)
    max_tokens: int = Field(gt=0)
```

`ge` es “mayor o igual”, `le` es “menor o igual”, `gt` es “mayor que”. Esto se escribe en el paso 2, en `unidad_1/pre_entrega/llm_client/schemas.py`.

### `BaseModel`

La clase de Pydantic de la que heredan `ChatMessage`, `ModelConfig` y `ModelResponse`.

### Validación

Revisar que los datos cumplen las reglas antes de usarlos. Pydantic la hace al construir el objeto. El enunciado la pide para los mensajes y para la configuración del modelo.

### asyncio

Módulo de la biblioteca estándar de Python para tareas que esperan (red, disco) sin frenar todo el programa. Hay un **event loop**: una cola que avanza las tareas que ya pueden seguir y deja en pausa las que están esperando una respuesta.

### `async def`

Declara una corrutina. Llamarla no la ejecuta del todo: devuelve un objeto que el event loop tiene que correr. Por eso `generate` va a ser `async def generate(...)`.

### `await`

Pausa esa corrutina hasta que termine otra operación async, y mientras tanto el event loop puede atender otra cosa. `await client.chat.completions.create(...)` es la forma correcta de llamar a OpenAI. La versión síncrona dentro de una función `async` bloquea el event loop: el programa entero queda congelado mientras el modelo piensa. Ese es el error que el enunciado pide evitar.

### Event loop

El ciclo que administra las corrutinas. `asyncio.run(main())` lo crea, corre `main` y lo cierra.

### Corrutina

El resultado de llamar una función `async def`. Es la tarea pausable.

### Generador

Función que entrega valores de a uno con `yield`, en vez de armar la lista completa y devolverla. Gasta memoria de a poco y permite ir mostrando resultados.

### Generador asíncrono

Generador que además puede `await` entre un `yield` y el siguiente. Es el tipo de retorno del streaming: cada fragmento llega por la red y se entrega apenas aparece.

### `yield`

Entrega un valor y pausa la función. La próxima iteración sigue desde ahí. En streaming: `yield` de cada pedazo de texto del SDK.

### `async for`

Recorre un generador asíncrono. Es el `for` que vamos a usar para imprimir el stream.

### SDK

Software Development Kit. La librería oficial para hablar con una API sin armar los HTTP a mano. Los que pide el enunciado:

| Proveedor | SDK | Cliente async |
| --- | --- | --- |
| OpenAI | `openai` | `AsyncOpenAI` |
| Anthropic | `anthropic` | `AsyncAnthropic` |
| Gemini | `google-genai` | cliente async del mismo paquete |
| Hugging Face | `huggingface_hub` | `AsyncInferenceClient` |

### python-dotenv

Lee un archivo `.env` y carga esas variables en el proceso. `unidad_1/pre_entrega/main.py` lo va a usar para no escribir las API keys dentro del código.

### pip

Instalador de paquetes de Python. Equivale a `npm` para dependencias de Python.

### Entorno virtual (`venv`)

Carpeta con un Python y unas librerías aisladas del resto de la máquina. Así las versiones de `openai` o `pydantic` de este curso no pisan otros proyectos. Se crea en el paso 7.

### `requirements.txt`

Lista de librerías y versiones. Equivale al `dependencies` de un `package.json`. El enunciado pide `openai`, `anthropic`, `pydantic` y `python-dotenv`. Para Gemini y Hugging Face se suman `google-genai` y `huggingface_hub`.

---

## Frameworks que vas a escuchar en el curso

Estas librerías **no** hacen falta para la pre-entrega 1. El cliente llama a los SDK directo. Igual los vas a ver en clase, y conviene tener claro qué son para no mezclarlos con lo que estamos armando.

### LangChain

Framework para armar aplicaciones con LLMs: plantillas de prompt, cadenas de pasos, conexión a herramientas y a documentos. Te ahorra código repetido y, a cambio, mete sus propias abstracciones. Esta entrega practica la capa de abajo: el cliente async, que LangChain también termina usando por dentro.

### LangGraph

Librería del mismo equipo para agentes con estado. El flujo es un grafo: nodos (pasos) y aristas (a qué paso se sigue). Puede haber ciclos, por ejemplo “el modelo pidió una herramienta → se ejecuta → vuelve al modelo”. Sirve cuando un `await generate()` de una sola vez ya no alcanza.

### LangSmith

Plataforma para observar y evaluar esas apps: qué prompt se mandó, qué volvió, cuánto tardó, cuánto costó. Es observabilidad, no es el cliente.

### LlamaIndex

Framework enfocado en RAG: cargar documentos, partirlos en chunks, indexarlos y preguntarles. Otra capa por encima de un LLM. Tampoco entra en esta entrega.

### MCP (Model Context Protocol)

Protocolo para conectar un modelo o un agente con herramientas y datos externos de una forma estándar. Lo vas a ver en Cursor y en integraciones. No es parte del cliente de esta pre-entrega.

---

## APIs, cuentas y errores

### API

Interfaz para que un programa use un servicio. Acá, las APIs HTTP de OpenAI, Anthropic, Google y Hugging Face.

### Endpoint

La URL concreta de una operación. Por ejemplo, el de chat de OpenAI vive bajo `https://api.openai.com/v1`. El SDK arma esa URL. Casi nunca la escribimos nosotros.

### API key

Clave secreta que demuestra que la cuenta sos vos. Viaja en un header del pedido. Va en `.env`, nunca en el código ni en Git. Si se filtra, se rota en el panel del proveedor.

| Variable | Dónde se crea |
| --- | --- |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) |
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `HF_TOKEN` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

### Variable de entorno

Valor que vive fuera del código, en el sistema o en `.env`. `LLM_PROVIDER=gemini` elige el proveedor sin tocar `unidad_1/pre_entrega/main.py`.

### `.env`

Archivo local `CLAVE=valor`. `.env.example` es la plantilla, sin secretos, y sí se sube al repo. `.env` está en `.gitignore`.

### HTTP

El protocolo de la llamada. El SDK lo habla por vos. Estos códigos son los que vamos a traducir a errores controlados:

| Código | Qué pasó | Error nuestro |
| --- | --- | --- |
| `401` o `403` | Key ausente o inválida | `auth` |
| `429` | Rate limit: demasiadas llamadas, o sin cuota | `rate_limit` |
| `500` y cortes de red | Falla del servicio o de la conexión | `network` o `provider` |

### Rate limit

Límite de cuántas llamadas (o tokens) podés hacer en una ventana de tiempo. La API responde `429`. El cliente va a esperar un poco y reintentar. Si sigue fallando, devuelve un error estructurado. El programa no se cae.

### Cuota

El crédito o el tope de tu plan. Se agota distinto del rate limit: reintentar al instante no lo arregla. También tiene que terminar en un error controlado.

### Retry

Volver a intentar una llamada que falló por algo transitorio (red o `429`). Un reintento con espera creciente se llama **backoff**: 1 segundo, después 2, después 4. Una key inválida no se reintenta.

### Excepción

El mecanismo de Python para señalar un error. Si nadie la captura, el programa se corta. El enunciado pide capturar las de red y de rate limit. En este diseño se convierten en un `ModelResponse` con el error, o en una excepción propia que `unidad_1/pre_entrega/main.py` sí espera.

### Provider (proveedor)

La empresa o plataforma que hospeda el modelo: OpenAI, Anthropic, Google, Hugging Face. `LLM_PROVIDER` elige uno.

---

## Piezas de nuestro código

### `ChatMessage`

Esquema Pydantic de un mensaje: `role` y `content`.

### `ModelConfig`

Esquema de la llamada: modelo, `temperature` (0 a 2), `max_tokens` (entero mayor que 0).

### `ModelResponse`

Esquema de lo que vuelve: texto, proveedor, modelo, y si la llamada salió bien o con un error controlado.

### `BaseLLMClient`

Clase abstracta. Define el contrato: `generate()` y `stream()`. No llama a ninguna API. Los cuatro clientes heredan de ella.

### Clase abstracta

Clase que no se instancia directo. Obliga a las hijas a implementar ciertos métodos. Así `unidad_1/pre_entrega/main.py` puede tratar a cualquier proveedor como un `BaseLLMClient`.

### Herencia

`OpenAIClient(BaseLLMClient)` quiere decir que el cliente de OpenAI es un `BaseLLMClient` y reemplaza `generate` y `stream` con la llamada real al SDK.

### `AsyncLLMManager`

La fachada. Lee `LLM_PROVIDER`, construye el cliente que corresponda y expone `generate` y `stream`. El resto del programa habla con el manager, no con cada SDK.

### Interfaz común

El conjunto de métodos que todos los proveedores cumplen. Cambiar de OpenAI a Gemini es cambiar la configuración, no el código de la pregunta.

### Event loop bloqueado

El bug de usar el cliente síncrono (`OpenAI()` en vez de `AsyncOpenAI()`) dentro de una función `async`. La llamada es correcta en apariencia y el programa queda tieso hasta que la API responde. La versión que vamos a usar es siempre la async, con `await`.
