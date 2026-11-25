import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // The ported design pages rely on browser default element styles (as in the design),
  // so Tailwind's reset is off; utilities still work everywhere.
  corePlugins: { preflight: false },
  theme: {
    extend: {
      colors: {
        // Same scale as kivartUI, centred on the website's rose accent.
        primary: {
          50: "#FBEFF2",
          100: "#F6E6EB",
          200: "#F1E3E7",
          300: "#F4C6D3",
          400: "#E3C9D0",
          500: "#C22B54",
          600: "#A8214A",
          700: "#8d1c3b",
          800: "#71142f",
          900: "#5c1126",
        },
        ink: {
          DEFAULT: "#1E1B1D",
          700: "#3D3438",
          500: "#6B5A60",
          300: "#CFC3C7",
        },
        blush: "#EBD5DB",
      },
      fontFamily: {
        sans: ["Poppins", "system-ui", "sans-serif"],
        display: ["Marcellus", "Georgia", "serif"],
        inter: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
