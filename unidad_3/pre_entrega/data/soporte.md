# Soporte de AndesPay

El soporte atiende el checkout cuando la caja no cobra o cuando un pedido confirmado no aparece. Esta nota dice por dónde se pide ayuda y qué datos hay que llevar. No incluye precios, planes comerciales ni el nombre de las personas que responden.

El canal es un solo correo: soporte@andespay.example. No hay teléfono ni chat. El correo se lee de lunes a viernes, de nueve de la mañana a seis de la tarde, hora de Chile. Un mensaje que llega el sábado se abre el lunes. No hay guardia de fin de semana.

Para que el pedido de ayuda sirva, el mensaje tiene que traer tres datos: el número de pedido si ya se cobró, la hora aproximada del intento y el mensaje de error que vio el cliente. Sin el número de pedido, soporte solo puede mirar si la caja estaba en pausa. No puede buscar una compra en el aire.

Soporte no rehace un cobro. Si Redis estaba caído, la persona tiene que volver a armar el carrito cuando la caja responda. Si PostgreSQL rechazó la escritura y la sesión sigue abierta, el cliente puede confirmar otra vez desde la misma sesión, dentro de los treinta minutos. Soporte no escribe pedidos a mano en la base.

Tampoco resuelve temas que no están en el checkout. No cambia precios, no crea cuentas de cliente y no explica planes. Si el mensaje pregunta cuánto sale un plan o quién dirige la empresa, la respuesta de soporte es que eso no está en su alcance. Esas preguntas no tienen ficha en AndesPay.

El cierre de un caso queda anotado con el número de pedido y una de estas tres marcas: `caja_en_pausa`, `pedido_no_persistido` o `resuelto`. No se usa otra marca. `resuelto` solo se escribe cuando el cliente pudo cobrar o pudo ver el pedido en PostgreSQL.
