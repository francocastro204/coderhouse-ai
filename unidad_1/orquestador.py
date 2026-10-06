"""Ejercicio opcional de la Unidad 1: orquestador concurrente de modelos.

No llama a ninguna API. Las esperas son asyncio.sleep, que simula la red
sin bloquear el programa. Hay dos partes:

1. Tres modelos se disparan juntos con asyncio.gather. Un timeout de 2
   segundos corta la ejecución total si alguna tarda de más.
2. Diez simulaciones se encolan, y un semáforo deja correr solo 2 a la vez.
"""

import asyncio
import time

INICIO = time.perf_counter()


def marca() -> str:
    """Segundos desde que arrancó el programa, para leer el orden en el log."""
    return f"{time.perf_counter() - INICIO:5.2f}s"


async def gpt_4_call() -> str:
    print(f"[{marca()}] gpt_4_call inició", flush=True)
    await asyncio.sleep(0.4)
    print(f"[{marca()}] gpt_4_call terminó", flush=True)
    return "respuesta de gpt-4"


async def claude_3_call() -> str:
    print(f"[{marca()}] claude_3_call inició", flush=True)
    await asyncio.sleep(0.8)
    print(f"[{marca()}] claude_3_call terminó", flush=True)
    return "respuesta de claude"


async def local_llama_call() -> str:
    print(f"[{marca()}] local_llama_call inició", flush=True)
    await asyncio.sleep(3.0)
    print(f"[{marca()}] local_llama_call terminó", flush=True)
    return "respuesta de llama"


async def tres_en_paralelo() -> None:
    """Dispara los tres modelos a la vez y corta todo el grupo a los 2 segundos."""
    print("Parte 1. Tres modelos con gather. Timeout de 2 segundos sobre el total.", flush=True)
    try:
        async with asyncio.timeout(2.0):
            await asyncio.gather(
                gpt_4_call(),
                claude_3_call(),
                local_llama_call(),
            )
    except TimeoutError:
        print(f"[{marca()}] TimeoutError: la ejecución superó los 2 segundos.", flush=True)
        print("El programa no se detiene. Sigue con el semáforo.", flush=True)


async def simulacion(numero: int, semaforo: asyncio.Semaphore, en_curso: list[int]) -> None:
    """Una llamada falsa. El semáforo impide que haya más de 2 activas."""
    async with semaforo:
        en_curso[0] += 1
        print(
            f"[{marca()}] simulación {numero:02d} inicia | en curso: {en_curso[0]}",
            flush=True,
        )
        await asyncio.sleep(0.4)
        en_curso[0] -= 1
        print(
            f"[{marca()}] simulación {numero:02d} termina | en curso: {en_curso[0]}",
            flush=True,
        )


async def lote_con_semaforo() -> None:
    """Diez llamadas encoladas. Solo dos pueden estar dentro del semáforo."""
    print(flush=True)
    print("Parte 2. Diez simulaciones. Semáforo de 2.", flush=True)
    semaforo = asyncio.Semaphore(2)
    en_curso = [0]
    await asyncio.gather(
        *(simulacion(numero, semaforo, en_curso) for numero in range(1, 11))
    )


async def main() -> None:
    await tres_en_paralelo()
    await lote_con_semaforo()
    print(f"[{marca()}] Fin. El programa terminó por su cuenta.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
