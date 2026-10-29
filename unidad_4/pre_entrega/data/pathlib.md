# pathlib

pathlib modela una ruta como un objeto, no como un string que hay que concatenar a mano. La clase central es Path. `Path("notas") / "unidad.md"` arma la ruta con el separador del sistema operativo. En Windows usa barra invertida y en el resto barra normal, sin que el código tenga que preguntarlo.

`Path.iterdir` recorre una carpeta. Devuelve un generador de Path, uno por cada entrada directa. No entra en las subcarpetas. Sirve para listar lo que hay en ese nivel: archivos, otras carpetas y enlaces. Si se necesita el árbol completo, el método es `Path.rglob`, que sí desciende. Confundir iterdir con rglob hace que un script se salte directorios o, al revés, que visite medio disco.

`Path.suffix` es el sufijo del archivo, con el punto incluido. Para `informe.tar.gz` el suffix es `.gz`. El nombre completo sin directorios está en `Path.name`, y el tronco sin el último sufijo está en `Path.stem`. Esas tres propiedades evitan los recortes con `split` que se rompen cuando la ruta trae más de un punto.

Leer y escribir también viven en el objeto. `Path.read_text` devuelve el contenido como string y `Path.write_text` lo reemplaza. Para bytes están `read_bytes` y `write_bytes`. El encoding por defecto de read_text es el del sistema, así que en un proyecto conviene pasarlo siempre: `read_text(encoding="utf-8")`. Si el archivo no existe, read_text lanza `FileNotFoundError`. Antes se puede preguntar con `Path.exists` o, más preciso, con `Path.is_file`.

`Path.mkdir` crea la carpeta. Con `parents=True` crea también a los padres que falten. Con `exist_ok=True` no falla si la carpeta ya está. Sin esas dos banderas, un script de instalación se cae la segunda vez que corre o cuando el directorio intermedio no fue creado.

Path también sabe resolver rutas relativas. `Path.cwd` es la carpeta desde la que se lanzó el proceso, que no siempre es la carpeta del archivo `.py`. `Path(__file__).resolve().parent` sí apunta a la carpeta del módulo. Mezclar las dos es la causa típica de un programa que encuentra los datos en la terminal y no los encuentra cuando lo llama otro script.

Para borrar, `Path.unlink` elimina un archivo y `Path.rmdir` elimina una carpeta vacía. Ninguno de los dos baja por el árbol. pathlib no trae un "borrá todo" a propósito: esa operación se combina con iterdir y se revisa qué se va a sacar. La idea de la librería es que la ruta sea un valor con operaciones claras, no una cadena que se va pegando con barras.
