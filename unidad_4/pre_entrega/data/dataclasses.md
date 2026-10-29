# dataclasses

dataclasses genera el código repetido de una clase que sobre todo guarda datos. El decorador `@dataclass` escribe `__init__`, `__repr__` y `__eq__` a partir de las anotaciones. Dos instancias con los mismos valores comparan igual. El repr muestra los campos, así que un print en un error sirve para ver el contenido sin un método hecho a mano.

Los campos se declaran como atributos de clase con tipo. `nombre: str` es obligatorio en el `__init__` generado. `edad: int = 0` tiene default. El orden importa igual que en una función: un campo sin default no puede ir después de uno que sí lo tiene.

El problema del valor mutable se resuelve con `field`. `etiquetas: list[str] = field(default_factory=list)` llama a `list` en cada instancia nueva. Si se escribiera `etiquetas: list[str] = []`, todas las instancias compartirían esa lista y un append en una se vería en la otra. `field` también acepta `compare=False` para dejar un campo fuera del `__eq__`, o `repr=False` para ocultarlo del texto, por ejemplo una contraseña.

`asdict` convierte la instancia en un diccionario. Recorre los campos y, si un campo es otra dataclass, también la convierte. `astuple` hace lo mismo con una tupla, en el orden de declaración. Sirven para salir hacia JSON o hacia una fila, sin escribir un método `to_dict` por clase. Hay que tener cuidado con los objetos que no son datos: asdict no sabe convertir un archivo abierto ni una conexión.

`frozen=True` hace la instancia inmutable. Asignar un campo después de crearla lanza `FrozenInstanceError`. Una dataclass congelada puede ser clave de un diccionario, porque el hash queda definido. Sin frozen, el hash no se genera: un objeto que puede cambiar no debe ser clave, porque el diccionario lo perdería.

`slots=True` usa `__slots__` y la instancia no tiene `__dict__`. Ocupa menos memoria cuando hay muchas, y rechaza atributos que no fueron declarados. No se combina bien con herencia múltiple de otras clases que también usen slots de forma desordenada. Para un registro simple, slots y frozen juntos dejan un valor chico y fijo.

Una dataclass no valida. Si el tipo dice `int` y le pasan un string, lo guarda igual. La anotación es para el lector y para el chequeador, no para una conversión. Cuando el dato viene de afuera y hay que rechazarlo, el lugar es un modelo que valide. Adentro del programa, cuando el valor ya es confiable, la dataclass evita el boilerplate del `__init__` y deja `asdict` para sacarlo hacia afuera.
