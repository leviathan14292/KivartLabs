import type { Metadata } from "next";
import { KataLogKraftPage } from "@/components/site";

export const metadata: Metadata = { title: "KataLogKraft — White-label Catalogue Builder" };

export default function Page() {
  return <KataLogKraftPage />;
}
