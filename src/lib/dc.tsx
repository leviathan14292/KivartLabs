import React from "react";

/**
 * Base class for the ported design pages. A page keeps its state in
 * `this.state`, computes everything its markup needs in `renderVals()`,
 * and `render()` (added by the port) reads those values.
 */
export class DCLogic<P = Record<string, unknown>, S = any> extends React.Component<P, S> {
  private dcMounted = false;
  private dcPending: Array<Parameters<React.Component<P, S>["setState"]>[0]> = [];

  renderVals(): Record<string, unknown> {
    return {};
  }

  // The pages start timers and data loads from their constructors, which can
  // call setState before React has mounted them. Hold those updates and
  // apply them on mount instead of dropping them.
  setState(update: Parameters<React.Component<P, S>["setState"]>[0], cb?: () => void) {
    if (this.dcMounted) {
      super.setState(update, cb);
    } else {
      this.dcPending.push(update);
    }
  }

  componentDidMount() {
    this.dcMounted = true;
    const pending = this.dcPending;
    this.dcPending = [];
    pending.forEach((u) => super.setState(u));
  }

  componentWillUnmount() {
    this.dcMounted = false;
  }
}

/** Turn an inline CSS string ("color: red; font-size: 12px") into a React style object. */
export function css(text: string | null | undefined): React.CSSProperties {
  const out: Record<string, string> = {};
  if (!text) return out;
  let depth = 0;
  let cur = "";
  const decls: string[] = [];
  for (const ch of String(text)) {
    if (ch === "(") depth++;
    if (ch === ")") depth--;
    if (ch === ";" && depth === 0) {
      decls.push(cur);
      cur = "";
    } else cur += ch;
  }
  decls.push(cur);
  for (const d of decls) {
    const i = d.indexOf(":");
    if (i < 0) continue;
    const prop = d.slice(0, i).trim();
    const value = d.slice(i + 1).trim();
    if (!prop || value === "") continue;
    const key = prop.startsWith("--")
      ? prop
      : prop.replace(/^-(webkit|moz|ms)-/, (_m, v: string) => v.charAt(0).toUpperCase() + v.slice(1) + "-")
          .replace(/-([a-z])/g, (_m, c: string) => c.toUpperCase());
    out[key] = value;
  }
  return out as React.CSSProperties;
}
