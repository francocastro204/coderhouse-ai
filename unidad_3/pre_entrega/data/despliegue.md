# Cómo se publica AndesPay

AndesPay se publica como tres procesos separados. No es un solo programa gigante. Esta nota dice en qué orden se encienden y qué se considera un despliegue terminado. No dice cuánto cuesta operarlo ni quién firma el pase.

El orden es fijo. Primero PostgreSQL, porque sin el archivo de pedidos no tiene sentido abrir la caja. Después Redis, porque sin sesión no hay carrito. Al final FastAPI, que necesita a las otras dos para arrancar. Si FastAPI levanta antes y no llega a Redis o a PostgreSQL, el proceso termina con el error `dependencia_ausente` y no queda escuchando pedidos.

Cada proceso corre en su propio contenedor. El contenedor de la API se construye a partir del código de FastAPI. El de Redis y el de PostgreSQL usan las imágenes habituales de cada uno, sin modificaciones. No se mezclan los tres en una sola imagen. Así se puede reiniciar la API sin apagar las bases.

Un despliegue termina cuando las tres comprobaciones pasan. PostgreSQL acepta una consulta simple. Redis responde al ping. FastAPI responde en la ruta `/salud` con el texto `ok`. Si falta una de las tres, el despliegue se considera fallido y no se manda tráfico nuevo. El tráfico viejo sigue en la versión anterior hasta que las tres den bien.

No hay ventana de publicación los domingos. El pase se hace de lunes a viernes, después de las diez de la mañana y antes de las cuatro de la tarde, hora de Chile. Fuera de ese horario el sistema puede seguir prendido, pero no se publica una versión nueva. Esa regla es de operación, no de precio.

La versión que está atendiendo se identifica con la etiqueta del contenedor de FastAPI. Esa etiqueta es un número, por ejemplo `2026.10.1`. No es el nombre de una persona ni el de un plan comercial. Para saber qué está en producción se mira esa etiqueta, no un documento de ventas.
