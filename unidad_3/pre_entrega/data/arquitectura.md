# Arquitectura de AndesPay

AndesPay es el checkout interno. No es un producto que se venda al público: es el sistema con el que la tienda cobra un pedido. Esta nota describe las tres piezas que lo sostienen y qué guarda cada una. No habla de precios, planes ni de personas del equipo.

La puerta de entrada es una API escrita en FastAPI. Recibe el pedido del cliente, valida que el carrito no esté vacío y que el medio de pago venga informado, y recién entonces sigue. FastAPI no guarda el pedido en memoria. Si el proceso se reinicia, lo que no se haya escrito en la base desaparece. Por eso la API es deliberadamente corta: recibe, valida, delega y responde.

Las sesiones viven en Redis. Una sesión es el carrito abierto y el identificador del cliente mientras todavía no pagó. Redis se eligió porque esa información se lee muchas veces y se puede perder sin romper la historia de la tienda: el cliente arma el carrito de nuevo. La clave de cada sesión dura treinta minutos. Si el cliente no confirma el pago en ese plazo, Redis borra la clave y el carrito queda vacío. No hay copia de la sesión en otro lado.

Los pedidos confirmados viven en PostgreSQL. Ahí queda el número de pedido, el monto ya cobrado, los productos y el estado. El estado arranca en `pagado` y pasa a `preparando` cuando el depósito lo toma. PostgreSQL es la pieza que no se puede reconstruir desde cero. Un pedido confirmado no se vuelve a pedir a Redis ni a FastAPI. Si alguien quiere saber qué compró un cliente la semana pasada, la respuesta está en PostgreSQL y en ningún otro sitio.

El recorrido de un cobro es este. El cliente arma el carrito y FastAPI lo guarda como sesión en Redis. Al confirmar, FastAPI lee esa sesión, cobra y escribe el pedido en PostgreSQL. Cuando PostgreSQL confirma la escritura, FastAPI borra la sesión de Redis. Si PostgreSQL rechaza la escritura, la sesión sigue en Redis y el cliente puede reintentar. No se cobra dos veces: el número de pedido se genera antes de escribir y PostgreSQL rechaza un número repetido.

FastAPI, Redis y PostgreSQL no se reemplazan entre sí. FastAPI no es una base de datos. Redis no es el archivo histórico. PostgreSQL no guarda el carrito a medio armar. Esa separación es la arquitectura. Cualquier pregunta sobre dónde vive un dato se responde con esta regla: lo que todavía no se pagó está en Redis; lo que ya se pagó está en PostgreSQL; la API solo coordina.
