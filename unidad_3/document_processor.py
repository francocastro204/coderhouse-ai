import re
import tiktoken
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    def __init__(
        self,
        model_encoding: str = "cl100k_base",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        # El tokenizer parte el texto en tokens y nos deja contarlos.
        # cl100k_base es el diccionario de cortes. encode() devuelve un número por token.
        self.tokenizer = tiktoken.get_encoding(model_encoding)

        # Debe usar una función personalizada para medir longitud por TOKENS, no caracteres.
        # chunk_size es el máximo por fragmento. chunk_overlap repite el final del anterior.
        # separators corta primero por párrafo, después por línea, punto, espacio y al final donde pueda.
        # En un texto muy denso se puede cambiar ese orden y ver dónde cae el corte.
        # El tamaño del fragmento cambia el vector: uno corto es una idea, uno largo mezcla varias.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.calculate_tokens,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def clean_text(self, text: str) -> str:
        """Limpia el texto eliminando espacios duplicados y saltos de línea innecesarios."""
        # Borra el encabezado repetido de cada página. Los saltos de línea se quedan.
        sin_encabezado = re.sub(
            r"^ACME S\.A\. — Manual interno — Pág\. \d+\n?",
            "",
            text,
            flags=re.MULTILINE,
        )
        # ■+ saca los cuadrados negros. [ \t]{2,} deja un solo espacio y no toca los \n.
        sin_basura = re.sub(r"■+", "", sin_encabezado)
        sin_espacios = re.sub(r"[ \t]{2,}", " ", sin_basura)
        # Tres saltos o más quedan en un solo salto doble, entre párrafos.
        return re.sub(r"\n{3,}", "\n\n", sin_espacios).strip()

    def calculate_tokens(self, text: str) -> int:
        """Calcula la cantidad de tokens usando el tokenizer de tiktoken."""
        # encode() devuelve la lista de tokens. len() cuenta cuántos hay.
        return len(self.tokenizer.encode(text))

    def process_document(self, raw_text: str) -> List[str]:
        """Pipeline: Limpieza -> Fragmentación."""
        # Este método solo devuelve los chunks. El print queda afuera,
        # así se puede reutilizar sin escribir en la consola.
        # Primero se saca el ruido. El splitter tiene que ver párrafos, no encabezados.
        limpio = self.clean_text(raw_text)
        # split_text corta el texto ya limpio y devuelve la lista de fragmentos.
        return self.splitter.split_text(limpio)


if __name__ == "__main__":
    # Texto de prueba
    text = """ACME S.A. — Manual interno — Pág. 1
Política de devoluciones■■
Los clientes pueden devolver un producto dentro de los 30 días    corridos desde la compra, siempre que conserven el ticket.
ACME S.A. — Manual interno — Pág. 2
El reintegro se hace por el mismo medio de pago. Si la compra fue en efectivo, se entrega una nota de crédito.
Envíos
Los envíos dentro de la ciudad demoran 48 horas hábiles. Para el interior del país, el plazo es de 5 a 7 días hábiles y el costo depende del peso del paquete.
ACME S.A. — Manual interno — Pág. 3
Garantía
Todos los productos electrónicos tienen 12 meses de garantía. La garantía no cubre daños por mal uso ni golpes."""
    # 40 y 10 para ver el corte en este texto corto. El defecto de la clase es 500 y 50.
    processor = DocumentProcessor(chunk_size=40, chunk_overlap=10)
    chunks = processor.process_document(text)
    # El seguimiento se imprime acá, no dentro de la clase.
    for indice, chunk in enumerate(chunks, start=1):
        print(f"Chunk {indice}: {processor.calculate_tokens(chunk)} tokens")
        print(chunk)
        print("---")
    print(f"Chunks generados: {len(chunks)}")
