import type { Metadata } from "next";
import { HomePage } from "@/components/site";

export const metadata: Metadata = { title: "Kivart — Corporate & Wedding Gifting Home" };

export default function Page() {
  return <HomePage />;
}
