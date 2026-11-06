export type Unidad = {
  numero: number;
  titulo: string;
  estado: "lista" | "hoy" | "falta";
  idea: string;
  pasos: string[];
  codigo: string;
};

export const unidades: Unidad[] = [
  {
    numero: 1,
    titulo: "Hablar con un modelo",
    estado: "lista",
    idea: "Una sola puerta para varios modelos. Mientras uno espera, otro puede avanzar.",
    pasos: ["Pregunta", "Cliente", "Gemini"],
    codigo: `await manager.generate(pregunta)
# si falta la key, sigue con el otro`,
  },
  {
    numero: 2,
    titulo: "Una cadena con contrato",
    estado: "lista",
    idea: "El texto entra por un tubo y sale como un objeto, no como un párrafo suelto.",
    pasos: ["Prompt", "Modelo", "Objeto"],
    codigo: `cadena = prompt | modelo | parser
await cadena.ainvoke({"pregunta": "..."})`,
  },
  {
    numero: 3,
    titulo: "Memoria local",
    estado: "lista",
    idea: "Se corta el texto, se guarda en Chroma y la respuesta sale solo de esos trozos.",
    pasos: ["Notas", "Trozos", "Chroma"],
    codigo: `# si no está en las notas
respuesta = "No lo sé"`,
  },
  {
    numero: 4,
    titulo: "Memoria en la nube",
    estado: "lista",
    idea: "Pinecone guarda los vectores. La búsqueda mira el sentido y también las palabras.",
    pasos: ["Vector", "Palabra", "Top 5"],
    codigo: `where = {"source": "tech_blog"}
# el mismo id actualiza, no duplica`,
  },
  {
    numero: 5,
    titulo: "Un agente que vuelve atrás",
    estado: "lista",
    idea: "Ya no es una línea. Piensa, usa una herramienta y puede intentarlo de nuevo.",
    pasos: ["Piensa", "Herramienta", "Recuerda"],
    codigo: `agent → tools → agent
# mismo thread_id = misma charla`,
  },
  {
    numero: 6,
    titulo: "Varios agentes, un jefe",
    estado: "hoy",
    idea: "Un supervisor reparte el trabajo. Los especialistas hacen una sola cosa.",
    pasos: ["Supervisor", "Especialista", "Revisión"],
    codigo: `# el jefe no escribe el informe
# elige quién lo hace`,
  },
  {
    numero: 7,
    titulo: "Ver qué pasó",
    estado: "falta",
    idea: "Una API y un registro de cada paso, para no adivinar por qué respondió eso.",
    pasos: ["API", "Redis", "Traza"],
    codigo: `# cada llamada deja una huella
# se puede abrir y leer`,
  },
  {
    numero: 8,
    titulo: "Juntar todo",
    estado: "falta",
    idea: "Un solo sistema: recuerda, razona y se levanta con un comando.",
    pasos: ["RAG", "Agentes", "API"],
    codigo: `./run.sh
# local, sin nube obligatoria`,
  },
];

export const glosario: { palabra: string; significado: string }[] = [
  { palabra: "LLM", significado: "Un modelo que completa texto. No busca en internet solo." },
  { palabra: "Token", significado: "El pedazo con el que el modelo lee. No es lo mismo que una palabra." },
  { palabra: "Prompt", significado: "La instrucción que le das. El modelo responde a eso, no a lo que pensaste." },
  { palabra: "Async", significado: "Mientras espera la red, el programa puede hacer otra cosa." },
  { palabra: "LCEL", significado: "Unir piezas con |. Prompt, modelo y parser, en ese orden." },
  { palabra: "Pydantic", significado: "Un molde. Si la respuesta no entra, no pasa." },
  { palabra: "Embedding", significado: "El texto convertido en números, para comparar significados." },
  { palabra: "Chunk", significado: "Un trozo del documento. Ni tan chico que pierda la idea, ni tan grande que la mezcle." },
  { palabra: "RAG", significado: "Buscar en tus notas y responder solo con lo que encontró." },
  { palabra: "Namespace", significado: "Una carpeta dentro del índice. Separa pruebas de lo real." },
  { palabra: "Upsert", significado: "Guardar. Si el id ya existe, lo actualiza." },
  { palabra: "Grafo", significado: "Cajas unidas por flechas. Una flecha puede volver atrás." },
  { palabra: "Herramienta", significado: "Una función real. El modelo la pide. El programa la ejecuta." },
  { palabra: "thread_id", significado: "El nombre de la conversación. El mismo id recuerda lo anterior." },
  { palabra: "Alucinación", significado: "El modelo inventa un dato con seguridad. Por eso el RAG dice «No lo sé»." },
];
