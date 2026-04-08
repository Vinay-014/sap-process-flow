import type { Metadata } from "next";
import "./globals.css";
import { WarRoom } from "@/components/WarRoom";

export const metadata: Metadata = {
  title: "AEGIS | Command Center",
  description: "Autonomous Executive & Geospatial Intelligence System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="grid-bg">
        <WarRoom />
      </body>
    </html>
  );
}
