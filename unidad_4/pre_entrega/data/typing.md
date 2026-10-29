# typing

typing anota el contrato de una función sin cambiar, en la mayoría de los casos, lo que pasa en tiempo de ejecución. Un chequeador como mypy o pyright lee esas anotaciones. Python, al correr, las ignora salvo que alguien las inspeccione con `typing.get_type_hints`.

`Optional[int]` significa `int | None`. No significa "este argumento se puede omitir". Esa confusión es muy común. Un parámetro opcional se declara con un valor por defecto. Optional solo dice que el valor admitido puede ser None. Desde Python 3.10 se puede escribir `int | None` y significa lo mismo. Optional sigue siendo útil cuando se quiere el nombre explícito.

`TypeVar` crea una variable de tipo. Sirve cuando la salida depende de la entrada y no se quiere fijar un tipo concreto. Una función `primero` que recibe una lista de T y devuelve T se anota con un TypeVar llamado T. Si se la llama con una lista de str, el chequeador sabe que el retorno es str. Sin TypeVar, el retorno cae en Any y se pierde el control.

`Protocol` describe un comportamiento, no una clase base. Un Protocol con un método `leer(self) -> str` lo cumple cualquier objeto que tenga ese método, aunque no herede de nadie. Es el tipado estructural, lo que en otros lenguajes se llama duck typing chequeado. Se usa cuando la librería no debe obligar al usuario a heredar de una clase suya.

`Union` junta alternativas. `Union[str, bytes]` acepta cualquiera de los dos. En 3.10 equivale a `str | bytes`. `Literal` fija valores concretos, por ejemplo `Literal["json", "csv"]`, y el chequeador marca un string que no esté en esa lista. `TypedDict` describe la forma de un diccionario: qué claves tiene y de qué tipo es cada una. No convierte el diccionario en un objeto. Solo documenta y chequea las claves.

`Callable` anota una función que se pasa como argumento. `Callable[[str, int], bool]` es una función que recibe un str y un int y devuelve bool. `Sequence` y `Mapping` son preferibles a `list` y `dict` cuando la función solo lee, porque aceptan tuplas y otros mapeos.

Las anotaciones de una clase se guardan en `__annotations__`. Si se postergan con `from __future__ import annotations`, quedan como strings y no se evalúan al definir la clase. Eso permite anotar una clase con su propio nombre antes de que termine de crearse. typing no valida datos en runtime. Para eso está otra librería. Acá el trabajo es decirle al chequeador qué forma tiene el programa.
