import type { Metadata } from "next";
import { BespokePage } from "@/components/site";

export const metadata: Metadata = { title: "Kivart — Bespoke Gifting" };

export default function Page() {
  return <BespokePage />;
}
