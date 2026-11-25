# Kivart Labs — website

Next.js 14 (App Router) + TypeScript + Tailwind, set up like `kivartUI`.

```bash
npm install
npm run dev   # http://localhost:3000
```

## Pages

| Route | Page | Design artboard |
| --- | --- | --- |
| `/` | Home | `design/Main.dc.html` |
| `/shop` | Shop with filters and shortlist | `design/Shop.dc.html` |
| `/katalogkraft` | KataLogKraft partner PDF builder | `design/Partner.dc.html` |
| `/bespoke` | Bespoke gifting brief | `design/Bespoke.dc.html` |
| `/shubh-aarambh` | Shubh Aarambh wedding collection | `design/ShubhAarambh.dc.html` |
| `/kivartklicks` | KivartKlicks camera roll | `design/Unboxed.dc.html` |

## How the pages are built

The pages come from the Kivart Labs redesign canvas. Each artboard there is a
component with its own state, handlers and markup, so it was ported as-is:

- `scripts/port_design.py` compiles each `design/*.dc.html` into
  `src/components/site/<Name>Page.tsx`. The page logic is kept as written, and
  the markup becomes JSX. Run `npm run port-design` to regenerate them, but this
  overwrites any hand edits in those files.
- `src/lib/dc.tsx` holds the small React base class (`DCLogic`) the pages extend.
- Images, videos and the extra SKU data live in `public/assets/`, named by their
  design asset id.
- Brand colours and fonts are in `tailwind.config.ts` (`primary`, `ink`, `blush`;
  Poppins, Marcellus, Inter). Tailwind's preflight reset is off so the ported
  pages keep the browser defaults they were designed against.
