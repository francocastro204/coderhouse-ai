"""Carga los textos de data/ en Chroma.

Desde la raíz del repo, con el entorno activo:

    python -m unidad_3.pre_entrega.ingest
"""

from unidad_3.pre_entrega.store import ingestar


def main() -> None:
    base = ingestar()
    print(f"Fragmentos en la colección: {base._collection.count()}")


if __name__ == "__main__":
    main()
