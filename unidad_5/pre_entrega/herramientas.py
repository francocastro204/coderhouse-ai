"""Pedidos simulados. Cada herramienta devuelve una sola parte.

contar_pedidos no trae el dinero. sumar_pedidos no trae la cantidad.
ultimo_pedido no sirve para ninguna de las dos. Si el cliente no existe,
la herramienta devuelve un error en texto y no corta el programa.
"""

import json

from langchain_core.tools import tool

PEDIDOS: dict[int, list[dict[str, str | int]]] = {
    102: [
        {"id": "P-901", "producto": "Teclado", "monto": 4500, "fecha": "2026-01-10"},
        {"id": "P-914", "producto": "Mouse", "monto": 2000, "fecha": "2026-02-02"},
        {"id": "P-933", "producto": "Monitor", "monto": 8000, "fecha": "2026-03-15"},
    ]
}


def _lista(cliente_id: int) -> list[dict[str, str | int]] | None:
    try:
        return PEDIDOS.get(int(cliente_id))
    except (TypeError, ValueError):
        return None


@tool
def contar_pedidos(cliente_id: int) -> str:
    """Cuenta los pedidos de un cliente.

    Usala cuando pregunten cuántos pedidos tuvo alguien.
    Devuelve solo la cantidad. No devuelve montos, ni el total, ni el
    último pedido. Si también preguntan el dinero, hace falta sumar_pedidos.
    Si el cliente no existe, devuelve un error para pedir el id de nuevo.
    """
    pedidos = _lista(cliente_id)
    if pedidos is None:
        return "Error: no existe el cliente. Pedile al usuario que confirme el id."
    return json.dumps({"cliente_id": int(cliente_id), "pedidos": len(pedidos)})


@tool
def sumar_pedidos(cliente_id: int) -> str:
    """Suma el dinero de los pedidos de un cliente.

    Usala cuando pregunten el total gastado.
    Devuelve solo el total. No devuelve la cantidad ni el último pedido.
    Si también preguntan cuántos pedidos son, hace falta contar_pedidos.
    Si el cliente no existe, devuelve un error para pedir el id de nuevo.
    """
    pedidos = _lista(cliente_id)
    if pedidos is None:
        return "Error: no existe el cliente. Pedile al usuario que confirme el id."
    total = sum(int(pedido["monto"]) for pedido in pedidos)
    return json.dumps({"cliente_id": int(cliente_id), "total": total})


@tool
def ultimo_pedido(cliente_id: int) -> str:
    """Trae el pedido más reciente de un cliente.

    Usala solo cuando pregunten por el último pedido.
    No sirve para contar pedidos ni para calcular el total.
    Devuelve id, producto, monto y fecha. Si el cliente no existe,
    devuelve un error para pedir el id de nuevo.
    """
    pedidos = _lista(cliente_id)
    if not pedidos:
        return "Error: no existe el cliente. Pedile al usuario que confirme el id."
    ultimo = max(pedidos, key=lambda pedido: str(pedido["fecha"]))
    return json.dumps({"cliente_id": int(cliente_id), **ultimo})


TOOLS = [contar_pedidos, sumar_pedidos, ultimo_pedido]
