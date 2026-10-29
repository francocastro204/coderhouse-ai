# logging

logging separa tres trabajos que a menudo se mezclan en un `print`. El Logger decide si el mensaje importa. El Handler decide a dónde va. El Formatter decide cómo se ve. Son tres objetos distintos y cada uno se configura solo.

Se obtiene un Logger con `logging.getLogger("tienda.pedidos")`. El nombre con puntos arma una jerarquía. Un mensaje emitido en `tienda.pedidos` también pueden verlo los handlers colgados de `tienda`, si la propagación está activa. Por eso una librería no llama a `logging.basicConfig`. Configura su Logger y deja que la aplicación dueña decida el destino. basicConfig en una librería le pisa el formato al programa que la importó.

El nivel filtra antes de armar el mensaje caro. Los niveles habituales son DEBUG, INFO, WARNING, ERROR y CRITICAL. Un Logger en INFO descarta DEBUG sin llamar al Handler. En producción se deja INFO o WARNING. En un incidente se baja a DEBUG el Logger de un módulo, no el de todo el proceso.

El Handler es el destino. `StreamHandler` escribe en la consola. `FileHandler` escribe en un archivo. Se pueden colgar los dos del mismo Logger y el mensaje sale por los dos lados. El Handler tiene su propio nivel. Así la consola muestra WARNING y el archivo guarda también INFO. Sin un Handler, y sin un padre que tenga uno, el mensaje no se ve. Ese es el síntoma de "agregué logs y no aparece nada".

El Formatter arma la línea. Recibe un patrón con `%(asctime)s`, `%(name)s`, `%(levelname)s` y `%(message)s`. El Handler usa ese Formatter. Cambiar el Formatter no cambia el nivel ni el destino: solo la forma del texto. Por eso Handler y Formatter no se reemplazan. El Handler sin Formatter escribe un texto por defecto. El Formatter sin Handler no tiene dónde imprimir.

`LoggerAdapter` agrega contexto fijo a un Logger, por ejemplo el id del pedido, sin tocar cada llamada. El adaptador implementa la misma interfaz de info, warning y error. En un request se crea un LoggerAdapter con los datos de esa petición y se lo pasa hacia abajo. Cuando el request termina, el adaptador se descarta y el Logger de fondo sigue igual.

`exc_info=True` en un error adjunta el traceback. Sin eso, el log dice que falló y no dice en qué línea. `logger.exception` dentro de un except hace lo mismo. El mensaje tiene que decir qué operación falló. El traceback dice dónde. Las dos cosas juntas alcanzan para encontrar el problema sin reproducirlo a ciegas.
