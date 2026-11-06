"use client";

import { FormEvent, useState } from "react";
import { glosario, unidades } from "@/lib/curso";

type Mensaje = { rol: "vos" | "ia"; texto: string; modelo?: string };

const etiqueta = { lista: "hecha", hoy: "hoy", falta: "falta" };

export default function Pagina() {
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [pregunta, setPregunta] = useState("");
  const [ocupado, setOcupado] = useState(false);

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    const texto = pregunta.trim();
    if (!texto || ocupado) return;
    setPregunta("");
    setMensajes((prev) => [...prev, { rol: "vos", texto }]);
    setOcupado(true);
    try {
      const respuesta = await fetch("/api/preguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: texto }),
      });
      const data = (await respuesta.json()) as { respuesta?: string; modelo?: string; error?: string };
      setMensajes((prev) => [
        ...prev,
        {
          rol: "ia",
          texto: data.respuesta || data.error || "No hubo respuesta.",
          modelo: data.modelo,
        },
      ]);
    } catch {
      setMensajes((prev) => [...prev, { rol: "ia", texto: "No pude llegar al servidor local." }]);
    } finally {
      setOcupado(false);
    }
  }

  return (
    <main className="pagina">
      <header className="cabeza">
        <div>
          <h1>El curso, en simple</h1>
          <p>Ocho módulos. Poco texto. Una pregunta al final.</p>
        </div>
        <nav className="nav">
          <a href="#linea">Línea</a>
          <a href="#palabras">Palabras</a>
          <a href="#preguntar">Preguntar</a>
        </nav>
      </header>

      <section className="bloque" id="linea">
        <h2>Línea</h2>
        <div className="linea">
          {unidades.map((unidad) => (
            <article className={`unidad ${unidad.estado}`} key={unidad.numero}>
              <div className="num">{unidad.numero}</div>
              <div className="carta">
                <span className="estado">{etiqueta[unidad.estado]}</span>
                <h3>{unidad.titulo}</h3>
                <p>{unidad.idea}</p>
                <div className="pasos">
                  {unidad.pasos.map((paso, i) => (
                    <span key={paso}>
                      {i > 0 && <span className="flecha"> → </span>}
                      <span className="paso">{paso}</span>
                    </span>
                  ))}
                </div>
                <pre>{unidad.codigo}</pre>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="bloque" id="palabras">
        <h2>Palabras</h2>
        <div className="palabras">
          {glosario.map((item) => (
            <article className="palabra" key={item.palabra}>
              <strong>{item.palabra}</strong>
              <span>{item.significado}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="bloque" id="preguntar">
        <h2>Preguntar</h2>
        <div className="chat">
          <div className="mensajes">
            {mensajes.length === 0 && (
              <p className="nota">Por ejemplo: ¿qué es un thread_id?</p>
            )}
            {mensajes.map((mensaje, i) => (
              <div className={`burbuja ${mensaje.rol}`} key={i}>
                {mensaje.texto}
                {mensaje.modelo && <span className="modelo">{mensaje.modelo}</span>}
              </div>
            ))}
          </div>
          <form onSubmit={enviar}>
            <input
              value={pregunta}
              onChange={(evento) => setPregunta(evento.target.value)}
              placeholder="Pregunta en simple"
              aria-label="Pregunta"
            />
            <button type="submit" disabled={ocupado}>
              {ocupado ? "..." : "Enviar"}
            </button>
          </form>
          <p className="nota">Corre en tu máquina. Primero Gemini. Si falla, Hugging Face.</p>
        </div>
      </section>
    </main>
  );
}
