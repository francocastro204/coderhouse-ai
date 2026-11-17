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
    estado: "lista",
    idea: "El jefe no responde. Manda a buscar la política y después a calcular.",
    pasos: ["Supervisor", "Investigador", "Analista"],
    codigo: `supervisor → investigador → analista
# sin las dos herramientas, no cierra`,
  },
  {
    numero: 7,
    titulo: "Ver qué pasó",
    estado: "lista",
    idea: "La API devuelve un job_id al toque. Redis guarda el estado y Phoenix muestra cada paso.",
    pasos: ["Job id", "Redis", "Pausa"],
    codigo: `POST /tasks → job_id
# si el reembolso saldría, espera un sí o un no`,
  },
  {
    numero: 8,
    titulo: "Juntar todo",
    estado: "hoy",
    idea: "Tienda Lumen: juegos en digital o en caja. El RAG, el supervisor y la API viven en otro repo.",
    pasos: ["Chroma", "Supervisor", "Un comando"],
    codigo: `# /Users/franco/developer/tienda-lumen
./run.sh`,
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
  { palabra: "Supervisor", significado: "El que reparte. No busca ni calcula: elige al especialista y decide si ya se puede cerrar." },
  { palabra: "Alucinación", significado: "El modelo inventa un dato con seguridad. Por eso el RAG dice «No lo sé»." },
];
