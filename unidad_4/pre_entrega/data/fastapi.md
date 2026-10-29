# FastAPI

FastAPI arma una API HTTP encima de Starlette y valida el cuerpo con Pydantic. El objeto que agrupa rutas es APIRouter. Se declara con un prefijo y un tag, y después se incluye en la aplicación con `include_router`. Así el archivo de usuarios no conoce el archivo de pedidos: cada área tiene su APIRouter y la aplicación solo los monta.

Un endpoint es una función decorada, por ejemplo `@router.get("/pedidos/{pedido_id}")`. El nombre del parámetro de la ruta tiene que coincidir con el de la función. Si el tipo es `int`, FastAPI rechaza un texto antes de entrar a la función y responde 422. El cuerpo de un POST se declara anotando un BaseModel. FastAPI lee el JSON, construye el modelo y, si Pydantic falla, también responde 422 con el detalle.

`Depends` inyecta una dependencia. En la firma se escribe `sesion: Sesion = Depends(abrir_sesion)`. FastAPI llama a `abrir_sesion` antes del endpoint y le pasa el resultado. Si `abrir_sesion` es una corrutina, la espera. Depends sirve para la base de datos, el usuario autenticado o una configuración. La misma dependencia se puede repetir en varios endpoints del APIRouter sin copiar el código de apertura y cierre.

Cuando la operación no puede seguir, se lanza `HTTPException`. Lleva un status y un detail. Un 404 es "no está", un 403 es "no podés" y un 409 es "el estado no deja hacer esto". No se usa HTTPException para un dato mal formado: eso ya lo cubre la validación del modelo. HTTPException es para una regla que solo se puede decidir después de mirar el sistema, por ejemplo que el pedido existe pero ya fue cobrado.

La aplicación principal es una instancia de `FastAPI`. Ahí se cuelga el APIRouter, se configura el título que aparece en la documentación automática y se declaran eventos de arranque. `/docs` muestra Swagger armado desde las anotaciones. Si una ruta no tiene tipo de respuesta, la documentación queda incompleta. `response_model` recorta la salida: aunque la función devuelva un objeto con más campos, al cliente le llega solo lo que el modelo declara.

FastAPI corre las funciones `async def` dentro del bucle de eventos. Una función `def` normal la manda a un threadpool, porque asume que puede bloquear. Mezclar una consulta síncrona lenta dentro de un `async def` traba a los demás pedidos. La regla es la de asyncio: si el endpoint espera a la red, es `async def` y usa un cliente asíncrono. Depends no cambia esa regla. Solo decide de dónde sale el argumento antes de que el endpoint empiece.
