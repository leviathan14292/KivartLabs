import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Kivart Labs — Corporate & Wedding Gifting",
  description:
    "B2B corporate gifting, bespoke kits, wedding collections and white-label catalogues from Kivart Labs.",
  keywords: ["corporate gifting", "wedding gifting", "bespoke gifts", "Kivart"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Marcellus&family=Inter:wght@400;600;700&display=swap"
        />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
