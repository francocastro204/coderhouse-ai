# 6.3 Estado compartido

Dos nodos async. Cada uno devuelve solo su campo. El investigador no toca la revisión. El revisor no toca los hallazgos.

## Qué recordar

- `researcher_output` es del investigador. `reviewer_output` es del revisor.
- El score vive en un contrato: de 0 a 1. Con 1.5, Pydantic lanza `ValidationError` y el programa lo atrapa.
- 0.9 es mayor que 0.8, así que la revisión sale aprobada.
- El `await asyncio.sleep(1)` es la espera. Mientras tanto el nodo no bloquea con una cuenta, solo cede el turno.

```bash
python unidad_6/6.3/estado.py
```

```mermaid
flowchart LR
  inicio([START]) --> investigador
  investigador -->|escribe researcher_output| revisor
  revisor -->|escribe reviewer_output| fin([END])
```
