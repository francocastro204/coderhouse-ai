# asyncio

asyncio es la librería de la biblioteca estándar para correr varias tareas de entrada y salida sin abrir un hilo por cada una. El corazón es el bucle de eventos. Ese bucle no ejecuta todo a la vez: avanza la corrutina que puede progresar y deja en espera a la que está bloqueada en la red o en el disco.

Una corrutina se declara con `async def`. Llamarla no la corre. Devuelve un objeto que el bucle todavía tiene que agendar. Para agendarla se usa `asyncio.create_task`. Esa llamada devuelve una Task. La Task es la unidad de trabajo que el bucle de eventos puede pausar y retomar. Si nadie guarda la referencia a la Task, el recolector de basura puede cancelarla antes de que termine.

Cuando hay varias Task independientes, `asyncio.gather` las espera juntas. Recibe las Task, o las corrutinas que convierte en Task, y devuelve una lista con el resultado de cada una, en el mismo orden en que se las pasaron. Si una Task lanza una excepción y no se pidió `return_exceptions=True`, gather cancela a las demás y propaga ese error. Con `return_exceptions=True`, el error viaja dentro de la lista, al lado de los resultados que sí salieron bien. Por eso gather no es un simple "esperá a todas": define qué pasa con el grupo cuando una pieza falla.

El bucle de eventos se arranca con `asyncio.run`. Esa función crea el bucle, corre la corrutina principal y al final cierra el bucle. Dentro de un programa que ya tiene un bucle, no se vuelve a llamar a `asyncio.run`. Ahí se espera con `await`. `await` solo es válido dentro de una corrutina. Pausa esa corrutina y le devuelve el control al bucle para que atienda otra Task.

Un error frecuente es mezclar tiempo bloqueante con el bucle. `time.sleep` congela el hilo entero, así que ninguna otra Task avanza. El equivalente que coopera es `asyncio.sleep`. Lo mismo pasa con una lectura de archivo síncrona muy larga: mientras esa llamada no suelta el hilo, el bucle de eventos no puede cambiar de Task. Para ese caso se manda el trabajo bloqueante a un ejecutor con `asyncio.to_thread`, y la Task que lo pidió queda en espera sin trabar al resto.

Otra pieza es el timeout. `asyncio.wait_for` envuelve una Task y la cancela si pasa el plazo. La cancelación llega como `CancelledError` dentro de la corrutina. Si la corrutina atrapa ese error y no lo vuelve a lanzar, la Task no se entera de que debía morir. El patrón sano es cerrar el recurso y dejar salir la cancelación.

asyncio no sirve para acelerar un cálculo de CPU. El bucle de eventos sigue siendo un solo hilo. Si la Task hace un cómputo pesado, las demás esperan. Ahí el trabajo se saca del bucle. Para muchas descargas, muchas consultas o muchos sockets, en cambio, unas pocas Task y un `asyncio.gather` alcanzan para superponer las esperas. La regla corta es esta: lo que espera a otro sistema se modela como Task; lo que solo calcula no se mete en el bucle de eventos.
