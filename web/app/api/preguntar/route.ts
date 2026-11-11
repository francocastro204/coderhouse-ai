import { readFileSync } from "node:fs";
import path from "node:path";
import { NextResponse } from "next/server";

const SISTEMA = `Respondes en español, muy corto, con palabras simples.
Solo contestas la pregunta. No agregues un resumen del curso.
Si no lo sabes, dilo. No inventes datos ni claves. Máximo 4 líneas.
Dato de este repo, por si preguntan: las unidades 1 a 6 ya están. La 6 es un supervisor que manda a un investigador a buscar una política y a un analista a calcular si el caso entra. La 7 y la 8 todavía no.`;

function leerEnv(): Record<string, string> {
  const archivo = path.join(process.cwd(), "..", ".env");
  const texto = readFileSync(archivo, "utf8");
  const vars: Record<string, string> = {};
  for (const linea of texto.split("\n")) {
    const limpia = linea.trim();
    if (!limpia || limpia.startsWith("#") || !limpia.includes("=")) continue;
    const corte = limpia.indexOf("=");
    vars[limpia.slice(0, corte).trim()] = limpia.slice(corte + 1).trim();
  }
  return vars;
}

async function gemini(pregunta: string, env: Record<string, string>) {
  const clave = env.GEMINI_API_KEY || env.GOOGLE_API_KEY;
  if (!clave) throw new Error("Falta GEMINI_API_KEY");
  const preferido = env.GEMINI_MODEL || "gemini-3.1-flash-lite";
  const modelos = preferido === "gemini-flash-lite-latest" ? [preferido] : [preferido, "gemini-flash-lite-latest"];
  let ultimo = "Gemini no respondió";
  for (const modelo of modelos) {
    const respuesta = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-goog-api-key": clave },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: SISTEMA }] },
          contents: [{ role: "user", parts: [{ text: pregunta }] }],
          generationConfig: { temperature: 0.3, maxOutputTokens: 400 },
        }),
      },
    );
    const data = (await respuesta.json()) as {
      candidates?: { content?: { parts?: { text?: string }[] } }[];
      error?: { message?: string };
    };
    if (!respuesta.ok) {
      ultimo = data.error?.message || "Gemini no respondió";
      if (respuesta.status === 503) continue;
      throw new Error(ultimo);
    }
    const texto = data.candidates?.[0]?.content?.parts?.map((parte) => parte.text || "").join("") || "";
    if (!texto) throw new Error("Gemini volvió vacío");
    return { respuesta: texto.trim(), modelo: `Gemini · ${modelo}` };
  }
  throw new Error(ultimo);
}

async function huggingFace(pregunta: string, env: Record<string, string>) {
  const token = env.HF_TOKEN || env.HUGGINGFACEHUB_API_TOKEN;
  if (!token) throw new Error("Falta HF_TOKEN");
  const modelo = env.HF_MODEL || "meta-llama/Llama-3.1-8B-Instruct";
  const respuesta = await fetch("https://router.huggingface.co/v1/chat/completions", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: modelo,
      messages: [
        { role: "system", content: SISTEMA },
        { role: "user", content: pregunta },
      ],
      max_tokens: 400,
    }),
  });
  if (respuesta.status === 402) throw new Error("Hugging Face no tiene crédito");
  const data = (await respuesta.json()) as {
    choices?: { message?: { content?: string } }[];
    error?: string;
  };
  if (!respuesta.ok) throw new Error(typeof data.error === "string" ? data.error : "Hugging Face no respondió");
  const texto = data.choices?.[0]?.message?.content?.trim() || "";
  if (!texto) throw new Error("Hugging Face volvió vacío");
  return { respuesta: texto, modelo: `Hugging Face · ${modelo}` };
}

export async function POST(request: Request) {
  const cuerpo = (await request.json()) as { pregunta?: string };
  const pregunta = cuerpo.pregunta?.trim() || "";
  if (!pregunta) return NextResponse.json({ error: "Escribe una pregunta." }, { status: 400 });

  let env: Record<string, string>;
  try {
    env = leerEnv();
  } catch {
    return NextResponse.json({ error: "No encontré el .env de la carpeta principal." }, { status: 500 });
  }

  try {
    return NextResponse.json(await gemini(pregunta, env));
  } catch (errorGemini) {
    try {
      return NextResponse.json(await huggingFace(pregunta, env));
    } catch (errorHF) {
      const geminiMsg = errorGemini instanceof Error ? errorGemini.message : "Gemini falló";
      const hfMsg = errorHF instanceof Error ? errorHF.message : "Hugging Face falló";
      return NextResponse.json(
        { error: `Gemini: ${geminiMsg}. Hugging Face: ${hfMsg}.` },
        { status: 502 },
      );
    }
  }
}
