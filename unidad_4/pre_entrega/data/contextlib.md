# contextlib

contextlib arma administradores de contexto, los bloques `with`, sin escribir una clase con `__enter__` y `__exit__`. El decorador principal es `@contextmanager`. Se pone sobre una función generadora. Lo que está antes del `yield` es la entrada. Lo que el `yield` entrega es el valor que recibe el `as`. Lo que está después del `yield` es la salida, y corre incluso si el bloque lanzó.

Un contextmanager de archivo temporal abre el archivo, hace `yield` del handle y en un `finally` lo cierra. El `finally` es obligatorio si hay algo que liberar. Sin él, una excepción en el bloque salta la limpieza. El decorador no adivina qué recurso hay que cerrar. Solo garantiza que, si la salida está escrita después del yield y dentro de un finally, se ejecuta al dejar el `with`.

`closing` envuelve un objeto que tiene método `close` y no sabe ser contexto. `with closing(pagina):` llama a `pagina.close()` al salir. Sirve para clientes viejos que abren y cierran con métodos, no con `with`. Si el objeto ya es un contexto, closing sobra y es mejor usarlo directo.

`ExitStack` junta una cantidad variable de contextos. Se usa cuando la lista se conoce en el momento, no cuando se escribe el código. Por ejemplo, abrir todos los archivos de una carpeta: un `with` normal no puede declarar n bloques. Se entra al ExitStack y, por cada archivo, se llama a `stack.enter_context(archivo)`. Al salir del stack, los contextos se cierran en orden inverso, aunque uno de ellos haya fallado al abrirse. Los que sí se abrieron no quedan colgados.

`stack.callback` registra una función para correr al final, aunque no sea un contexto. Es el lugar de un "al salir, borrá este temporal" cuando no vale la pena escribir un contextmanager entero. El callback no recibe el error. Si la limpieza tiene que saber si el bloque falló, hace falta un contextmanager con un `try` alrededor del yield.

`suppress` es un contexto que calla excepciones concretas. `with suppress(FileNotFoundError):` sigue de largo si el archivo no estaba. No es un `except` amplio. Solo calla las clases que se le pasaron. Usarlo para `Exception` esconde fallos de programación.

`nullcontext` entrega un contexto que no hace nada y devuelve el valor que se le pasó. Sirve en una función que a veces recibe un contexto de verdad y a veces no: se normaliza con nullcontext y el `with` de adentro queda escrito una sola vez.

La regla de contextlib es la misma que la del `with` escrito a mano. Entrar reserva, salir libera, y la liberación no depende de que el bloque haya llegado a la última línea. contextmanager, closing y ExitStack son tres formas de decir eso: una para una función, otra para un objeto con close, y otra para una lista que se arma en el momento.
