import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "El curso, en simple",
  description: "Línea de las unidades y un lugar para preguntar.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
