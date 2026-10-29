"""Mide Precision@5 y Recall@5 contra el golden set.

Recall@5: 1 si el documento esperado aparece entre los 5, si no 0.
Precision@5: qué fracción de esos 5 pertenece a ese documento.

Desde la raíz del repo, con el entorno activo:

    python -m unidad_4.pre_entrega.evaluate
"""

import json

from unidad_4.pre_entrega.config import GOLDEN, TOP_K
from unidad_4.pre_entrega.retriever import RAGSystem


def recall_at_k(ids_recuperados: list[str], esperado: str, k: int) -> float:
    """1 si el documento correcto está en el top k. Hay un solo relevante."""
    return 1.0 if esperado in ids_recuperados[:k] else 0.0


def precision_at_k(ids_recuperados: list[str], esperado: str, k: int) -> float:
    """Porcentaje de los k recuperados que vienen del documento esperado."""
    if k == 0:
        return 0.0
    utiles = sum(1 for documento_id in ids_recuperados[:k] if documento_id == esperado)
    return utiles / k


def main() -> None:
    preguntas = json.loads(GOLDEN.read_text(encoding="utf-8"))
    sistema = RAGSystem()
    recalls = []
    precisiones = []

    for item in preguntas:
        recuperados = sistema.buscar(item["pregunta"])
        ids = [documento.metadata.get("documento_id", "") for documento in recuperados]
        esperado = item["documento_id_esperado"]
        recall = recall_at_k(ids, esperado, TOP_K)
        precision = precision_at_k(ids, esperado, TOP_K)
        recalls.append(recall)
        precisiones.append(precision)
        print(f"Pregunta: {item['pregunta']}")
        print(f"  Esperado: {esperado}")
        print(f"  Recuperados: {', '.join(ids) if ids else '(ninguno)'}")
        print(f"  Recall@{TOP_K}: {recall:.2f}")
        print(f"  Precision@{TOP_K}: {precision:.2f}")

    print("---")
    print(f"Recall@{TOP_K} promedio: {sum(recalls) / len(recalls):.2f}")
    print(f"Precision@{TOP_K} promedio: {sum(precisiones) / len(precisiones):.2f}")


if __name__ == "__main__":
    main()
