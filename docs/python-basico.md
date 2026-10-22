# Python básico

Este archivo es una guía de lectura, no es código. Sirve para reconocer la sintaxis de los `.py` del repo si venís de JavaScript o TypeScript: funciones, comentarios, variables, constantes, `if`, operadores, clases y `async`. La comparación con JS y TS está al final.

Los archivos de Python terminan en `.py`.

Python 3.12 es la versión de esta pre-entrega. La sintaxis de acá es la de esa versión.

## Cómo se corre un archivo

```bash
python main.py
```

`python` es el programa. `main.py` es el archivo. Equivale a `node main.js`.

En este proyecto vamos a usar un entorno virtual (paso 7). Hasta entonces, alcanza con saber que el comando de arriba ejecuta un archivo de arriba hacia abajo, igual que un script de Node.

## La indentación es el bloque

En JavaScript un bloque va entre `{ }`. En Python el bloque es lo que está más a la derecha, con espacios.

```python
if edad >= 18:
    print("puede entrar")
    print("sigue dentro del if")
print("esto ya está afuera")
```

Se usan 4 espacios por nivel. Mezclar tabs y espacios rompe el archivo. Los dos puntos `:` abren el bloque: después de `if`, `for`, `def`, `class`, `try`.

## Comentarios

Una línea se comenta con `#`. Todo lo que sigue en esa línea lo ignora Python.

```python
# Esto es un comentario
temperatura = 0.2  # también se puede al final de una línea
```

Un comentario de varias líneas, pegado al inicio de un archivo, función o clase, es un **docstring**. Sirve de documentación. Va entre tres comillas.

```python
def generar(pregunta: str) -> str:
    """Pide una respuesta al modelo y devuelve el texto."""
    return pregunta
```

En este repo los `.py` arrancan con un docstring que dice qué va a hacer ese archivo.

## Variables

Una variable nace cuando le asignás un valor. No hay `let`, `const` ni `var`.

```python
nombre = "Ada"
edad = 36
activo = True
```

El tipo lo decide el valor, y puede cambiar después:

```python
valor = 1
valor = "ahora es texto"
```

Los nombres van en `snake_case`: `api_key`, `max_tokens`. Una clase va en `PascalCase`: `ChatMessage`, `OpenAIClient`.

## Constantes

Python no tiene `const`. Por convención, un nombre en `MAYUSCULAS` significa “no lo cambies”.

```python
TEMPERATURA_MAXIMA = 2
PROVEEDOR_POR_DEFECTO = "gemini"
```

El lenguaje igual te deja reasignarla. Es un acuerdo entre personas, igual que un `const` que alguien podría saltarse con un cast. En este proyecto las claves y los nombres de modelo viven en `.env`, y los límites (temperatura de 0 a 2) los va a vigilar Pydantic.

## Tipos que vas a ver

| Tipo | Ejemplo | Qué es |
| --- | --- | --- |
| `int` | `42` | Entero |
| `float` | `0.7` | Decimal. La temperatura es un float |
| `str` | `"hola"` | Texto |
| `bool` | `True`, `False` | Sí o no. Van con mayúscula |
| `None` | `None` | Ausencia de valor. Equivale a `null` |
| `list` | `["user", "assistant"]` | Lista ordenada. Equivale a un array |
| `dict` | `{"role": "user"}` | Pares clave-valor. Equivale a un objeto |
| `tuple` | `("openai", "gemini")` | Lista fija. No se suele modificar |

`True`, `False` y `None` siempre van con esa mayúscula. `true`, `false` y `null` son un error en Python.

Las anotaciones de tipo se escriben con `:` y el tipo de retorno con `->`. Documentan y las revisa el editor. Python las ignora al ejecutar, salvo que una librería (Pydantic, en nuestro caso) las use para validar.

```python
def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"
```

Eso se parece a TypeScript. La diferencia: TypeScript las chequea al compilar. Python, de fábrica, no.

## Texto

Comillas simples y dobles valen igual.

```python
frase = "¿Qué es la entropía?"
```

Un **f-string** mete variables dentro del texto. La `f` va pegada a la comilla.

```python
modelo = "gemini-3.8-flash"
print(f"Usando el modelo {modelo}")
```

Es el equivalente de `` `Usando el modelo ${modelo}` ``.

## Operadores

Aritméticos:

| Operador | Significado | Ejemplo |
| --- | --- | --- |
| `+` | Suma | `1 + 2` |
| `-` | Resta | `5 - 1` |
| `*` | Multiplicación | `3 * 4` |
| `/` | División (siempre decimal) | `5 / 2` da `2.5` |
| `//` | División entera | `5 // 2` da `2` |
| `%` | Resto | `5 % 2` da `1` |
| `**` | Potencia | `2 ** 3` da `8` |

Comparación:

| Operador | Significado |
| --- | --- |
| `==` | Igual |
| `!=` | Distinto |
| `<` `>` `<=` `>=` | Menor, mayor, menor o igual, mayor o igual |

En Python `==` compara el valor. No existe `===`.

Lógicos. Se escriben con palabras:

| Python | JavaScript | Significado |
| --- | --- | --- |
| `and` | `&&` | Las dos condiciones |
| `or` | `\|\|` | Al menos una |
| `not` | `!` | Lo contrario |

```python
if temperatura >= 0 and temperatura <= 2:
    print("temperatura válida")
```

Pertenencia:

```python
if proveedor in ("openai", "anthropic", "gemini", "huggingface"):
    print("proveedor conocido")
```

`in` pregunta si un valor está dentro de una lista, tupla o texto.

## if, elif, else

```python
proveedor = "gemini"

if proveedor == "openai":
    print("GPT")
elif proveedor == "anthropic":
    print("Claude")
elif proveedor == "gemini":
    print("Gemini")
else:
    print("otro")
```

`elif` es el `else if`. No van paréntesis obligatorios alrededor de la condición. Sí van los dos puntos y la indentación.

## for y while

`for` recorre una colección. No es el `for (i = 0; i < n; i++)` clásico.

```python
mensajes = ["hola", "chau"]

for mensaje in mensajes:
    print(mensaje)
```

Si necesitás el índice:

```python
for indice, mensaje in enumerate(mensajes):
    print(indice, mensaje)
```

`while` repite mientras la condición sea verdadera.

```python
intentos = 0
while intentos < 3:
    intentos = intentos + 1
```

`break` corta el ciclo. `continue` salta a la vuelta siguiente. Igual que en JavaScript.

## Funciones

```python
def armar_pregunta(texto: str) -> str:
    return f"Respondé breve: {texto}"


print(armar_pregunta("¿Qué es la entropía?"))
```

- `def` declara la función.
- Los parámetros van entre paréntesis.
- `return` devuelve un valor y termina la función. Sin `return`, la función devuelve `None`.
- Una función se llama con `nombre(...)`.

Parámetro con valor por defecto:

```python
def configurar(temperatura: float = 0.2, max_tokens: int = 300) -> None:
    print(temperatura, max_tokens)


configurar()
configurar(temperatura=0.7)
```

Cuando el argumento lleva el nombre (`temperatura=0.7`), el orden deja de importar. Lo vas a ver mucho en las llamadas a los SDK.

## Listas y diccionarios

Lista:

```python
roles = ["system", "user", "assistant"]
roles.append("tool")
primero = roles[0]
```

Los índices empiezan en `0`, igual que en JavaScript.

Diccionario:

```python
mensaje = {"role": "user", "content": "¿Qué es la entropía?"}
texto = mensaje["content"]
```

`mensaje["content"]` es `mensaje.content` en JavaScript. Si la clave no existe, Python lanza un error. Por eso en este proyecto los mensajes van a ser objetos de Pydantic, con campos fijos, en vez de diccionarios sueltos.

## Clases

Una clase es un molde. Un objeto es un ejemplar de ese molde.

```python
class ChatMessage:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def es_del_usuario(self) -> bool:
        return self.role == "user"


mensaje = ChatMessage("user", "¿Qué es la entropía?")
print(mensaje.es_del_usuario())
```

- `__init__` es el constructor.
- `self` es el objeto mismo. En JavaScript es `this`, y en Python hay que escribirlo en cada método.
- `mensaje.role` lee un atributo.

Herencia: una clase hija toma lo de la clase padre y puede reemplazar métodos.

```python
class Animal:
    def hablar(self) -> str:
        return "..."


class Perro(Animal):
    def hablar(self) -> str:
        return "guau"
```

`Perro(Animal)` significa “Perro hereda de Animal”. En este proyecto `OpenAIClient`, `AnthropicClient`, `GeminiClient` y `HuggingFaceClient` van a heredar de `BaseLLMClient`. El padre define `generate()` y `stream()`. Cada hijo los implementa a su manera.

## Errores: try y except

```python
try:
    numero = int("hola")
except ValueError:
    print("eso no es un número")
```

`try` / `except` es `try` / `catch`. Se puede nombrar el tipo de error para atrapar solo ese. Un `except Exception` atrapa casi todo, y en este proyecto lo vamos a usar en el borde de la llamada al modelo para devolver un error controlado.

`raise` lanza un error. Equivale a `throw`.

```python
raise ValueError("temperatura fuera de rango")
```

## import

Trae código de otro archivo o de una librería instalada.

```python
import os
from dotenv import load_dotenv
```

- `import os` trae el módulo entero. Se usa `os.getenv(...)`.
- `from dotenv import load_dotenv` trae una función puntual.

Un archivo `unidad_1/pre_entrega/llm_client/schemas.py` se importa así desde la raíz del proyecto:

```python
from unidad_1.pre_entrega.llm_client.schemas import ChatMessage
```

La carpeta necesita un `__init__.py` para que Python la trate como paquete. Ya está creado.

## async, en una página

Esto se usa en todo el cliente. El detalle está en el [glosario](glosario.md), en **asyncio**.

```python
import asyncio


async def preguntar() -> str:
    return "respuesta del modelo"


async def main() -> None:
    texto = await preguntar()
    print(texto)


asyncio.run(main())
```

- `async def` declara una función que se puede pausar.
- `await` espera un resultado de red (u otra operación async) sin congelar el programa.
- `asyncio.run(main())` arranca el programa. En `main.py` va a estar esta línea.

Un generador entrega valores de a uno con `yield`. Si además es async, quien lo recorre usa `async for`:

```python
async def stream():
    for pedazo in ["La ", "entropía ", "mide ", "desorden."]:
        yield pedazo


async def mostrar() -> None:
    async for pedazo in stream():
        print(pedazo, end="")
```

Ese es el mecanismo del modo streaming de la pre-entrega.

## Comparación con JavaScript y TypeScript

| Idea | JavaScript / TypeScript | Python |
| --- | --- | --- |
| Extensión | `.js`, `.ts`, `.tsx` | `.py` |
| Ejecutar | `node archivo.js` | `python archivo.py` |
| Bloque | `{ }` | Indentación y `:` |
| Comentario | `//` y `/* */` | `#` |
| Documentar | JSDoc `/** */` | Docstring `""" """` |
| Declarar variable | `let`, `const` | `nombre = valor` |
| Constante de verdad | `const` no se reasigna | No existe. `MAYUSCULAS` es convención |
| Sin valor | `null`, `undefined` | `None` |
| Booleanos | `true`, `false` | `True`, `False` |
| Y / o / no | `&&`, `\|\|`, `!` | `and`, `or`, `not` |
| Igualdad de valor | `===` (y `==` con coerción) | `==` |
| Condicional | `if (x) { } else if { }` | `if x: ... elif ... else:` |
| Función | `function f() {}` o `const f = () => {}` | `def f():` |
| Texto con variable | `` `Hola ${nombre}` `` | `f"Hola {nombre}"` |
| Array | `const xs = [1, 2]` | `xs = [1, 2]` (se llama lista) |
| Objeto | `{ role: "user" }` | `{"role": "user"}` (se llama dict). Las claves van entre comillas |
| Recorrer | `xs.forEach(x => ...)` | `for x in xs:` |
| Clase | `class Perro extends Animal` | `class Perro(Animal):` |
| El objeto actual | `this` | `self`, y hay que declararlo en el método |
| Constructor | `constructor()` | `def __init__(self):` |
| Error | `try / catch`, `throw` | `try / except`, `raise` |
| Módulos | `import` / `export` | `import` / `from ... import`. Lo que está en el archivo se puede importar |
| Tipos | TypeScript los exige al compilar | Las anotaciones documentan. Pydantic sí valida en ejecución |
| Interfaz | `interface` | Clase abstracta, o un modelo de Pydantic |
| Async | `async` / `await` | `async` / `await`. Misma idea |
| Dependencias | `npm`, `package.json` | `pip`, `requirements.txt` |
| Variables secretas | `.env` + una librería | `.env` + `python-dotenv` |
| Valor por defecto raro | Cuidado con objetos mutables en parámetros | Igual: un `[]` como default se comparte entre llamadas. Usar `None` y crear la lista adentro |

Lo que más cuesta al principio, viniendo de JS, suele ser la indentación, `self`, `True`/`None`, y que un diccionario no se accede con un punto. El `async`/`await` se lee casi igual.