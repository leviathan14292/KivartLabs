import type { Metadata } from "next";
import { KivartKlicksPage } from "@/components/site";

export const metadata: Metadata = { title: "Kivart — KivartKlicks" };

export default function Page() {
  return <KivartKlicksPage />;
}
