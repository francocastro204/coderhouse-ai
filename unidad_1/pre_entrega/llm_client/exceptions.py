"""Dónde viven los errores de una llamada.

El notebook del curso no corta el programa con una excepción. Cada cliente
atrapa el fallo del SDK (key inválida, red, rate limit) y lo devuelve
dentro de ModelResponse.error. main.py imprime ese texto y sigue.

Este archivo existe para dejar esa decisión escrita. No define clases
propias: el error controlado es el campo error de ModelResponse, en
unidad_1/pre_entrega/llm_client/schemas.py.
"""
