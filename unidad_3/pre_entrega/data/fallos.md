# Qué hace AndesPay cuando una pieza falla

Esta nota cubre solo las fallas de Redis, de PostgreSQL y de la API. No cubre precios, descuentos ni el nombre de quien opera el sistema.

Si Redis deja de responder, nadie puede pagar. El carrito abierto está solo ahí. FastAPI, al no poder leer la sesión, responde al cliente con el código 503 y el mensaje «el checkout está en pausa». No intenta cobrar con un carrito vacío ni inventa una sesión. Los pedidos que ya estaban en PostgreSQL siguen consultables, porque esa lectura no pasa por Redis. Lo que se corta es el cobro nuevo.

FastAPI reintenta la lectura de Redis dos veces, con una espera de un segundo entre intentos. Si las dos fallan, devuelve el 503 y no sigue. No hay una tercera copia del carrito. El cliente tiene que esperar a que Redis vuelva y armar el carrito otra vez si los treinta minutos de la clave ya pasaron.

Si PostgreSQL deja de responder en el momento de confirmar, el cobro no se da por hecho. FastAPI no borra la sesión de Redis. El cliente ve el mensaje «no pudimos registrar el pedido, tu carrito sigue abierto». El reintento de esa escritura es uno solo, a los dos segundos. Si también falla, se abandona y queda registrado un aviso en el log con el texto `pedido_no_persistido`. Ese aviso no es un pedido: es la marca de que no se escribió.

Si FastAPI se cae y Redis y PostgreSQL siguen arriba, no se pierde el archivo histórico ni el carrito que todavía no venció. Al volver la API, las sesiones vivas se retoman y los pedidos viejos se leen de PostgreSQL. No hay un modo degradado que cobre sin la API. Sin FastAPI no entra ningún pedido nuevo, aunque las bases estén sanas.

Una falla no se arregla cambiando de pieza. No se guarda el carrito en PostgreSQL «por mientras» ni se lee el historial desde Redis. Cada base tiene un trabajo. Cuando una no responde, se corta la operación que dependía de ella y se dice eso, en lugar de completar con datos de otra.
