# pydantic

Pydantic valida datos y los convierte en objetos. La clase base es BaseModel. Cada campo se anota con un tipo. Al construir el modelo, Pydantic revisa que el valor entre en ese tipo y, cuando puede, lo convierte. El string `"10"` asignado a un `int` termina siendo el entero 10. Si la conversión no es posible, la construcción falla.

El error es un `ValidationError`. No es una excepción genérica: trae una lista de fallos, con la ubicación del campo y el motivo. Un endpoint o un script de carga pueden recorrer esa lista y decir qué dato llegó mal, en vez de cortar con un mensaje opaco.

`field_validator` revisa un campo con una función propia, después de la conversión de tipo. Se declara como método de la clase, decorado con `@field_validator("edad")`. Recibe el valor ya convertido y devuelve el valor aceptado, o lanza si no sirve. Por ejemplo, un BaseModel de usuario puede tener un field_validator que rechace una edad negativa aunque el tipo `int` la hubiera dejado pasar. El validador no reemplaza al tipo. El tipo dice la forma y el field_validator dice la regla de negocio.

`Field` agrega restricciones al declarar el campo: `min_length`, `ge` para un número mínimo, un valor por defecto o una descripción. `Field(default_factory=list)` entrega una lista nueva en cada instancia. Poner `default=[]` compartiría la misma lista entre objetos, que es el mismo error de siempre con los valores mutables.

`model_validate` construye el modelo desde un diccionario. `model_dump` lo vuelve a convertir en diccionario, y `model_dump_json` en un string JSON. Esas dos salidas son las que se guardan o se mandan por la red. `model_config` cambia el comportamiento de la clase, por ejemplo para aceptar el modelo por alias o para prohibir campos extra.

Un BaseModel no es un dataclass. El dataclass guarda lo que le pasen. El BaseModel se niega a guardarlo si no cumple. Esa diferencia importa en el borde del sistema: la entrada de una API, un archivo de configuración o la respuesta de otro servicio. Ahí el ValidationError es la defensa. Adentro del programa, una vez que el dato ya es un BaseModel, el resto del código puede confiar en los tipos.

Pydantic v2 separa el validador de campo del validador de modelo. `model_validator` ve el objeto entero, cuando la regla cruza dos campos, como "la fecha de fin no puede ser anterior a la de inicio". field_validator sigue siendo el lugar de una regla de un solo campo. Usar uno u otro según el alcance evita validadores que leen atributos que todavía no existen.
