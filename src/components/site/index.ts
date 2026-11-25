"use client";

import dynamic from "next/dynamic";

// The pages read window, sessionStorage and media elements while they set up,
// so they render on the client only.
export const HomePage = dynamic(() => import("./HomePage"), { ssr: false });
export const ShopPage = dynamic(() => import("./ShopPage"), { ssr: false });
export const KataLogKraftPage = dynamic(() => import("./KataLogKraftPage"), { ssr: false });
export const BespokePage = dynamic(() => import("./BespokePage"), { ssr: false });
export const ShubhAarambhPage = dynamic(() => import("./ShubhAarambhPage"), { ssr: false });
export const KivartKlicksPage = dynamic(() => import("./KivartKlicksPage"), { ssr: false });
