import type { Metadata } from "next";
import { ShopPage } from "@/components/site";

export const metadata: Metadata = { title: "Kivart — Shop" };

export default function Page() {
  return <ShopPage />;
}
