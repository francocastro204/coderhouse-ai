"""Similitud coseno para el ejercicio opcional de la unidad 3.

Los vectores de abajo son un ejemplo numérico. No son los embeddings
de las oraciones del PDF: sirven para ver qué número devuelve la cuenta.
"""

from sklearn.metrics.pairwise import cosine_similarity


consulta = [[0.80, 0.10, 0.05]]
oracion_parecida = [[0.76, 0.18, 0.08]]
trampa = [[0.05, 0.90, 0.10]]

parecida = cosine_similarity(consulta, oracion_parecida)[0][0]
irrelevante = cosine_similarity(consulta, trampa)[0][0]

print(f"consulta vs oración del mismo tema: {parecida:.3f}")
print(f"consulta vs trampa de palabras:     {irrelevante:.3f}")
