"""Port the Kivart design artboards (design/*.dc.html) into React page components.

Each artboard is a Design Component: a template (<x-dc> markup with {{holes}},
<sc-if>, <sc-for>) plus a logic class (`class Component extends DCLogic`) whose
renderVals() feeds the template. DCLogic is a thin React.Component, so the
logic is kept as written and the template is compiled to JSX.

Output: src/components/site/<Name>Page.tsx (one client component per page).
Asset URLs (/_blob/<id>) are rewritten to /assets/<id>.<ext> in public/.

Usage: npm run port-design
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(ROOT, "design")
ASSETS = os.path.join(ROOT, "public", "assets")
OUT = os.path.join(ROOT, "src", "components", "site")

PAGES = {
    "Main.dc.html": ("HomePage", "/"),
    "Shop.dc.html": ("ShopPage", "/shop"),
    "Partner.dc.html": ("KataLogKraftPage", "/katalogkraft"),
    "Bespoke.dc.html": ("BespokePage", "/bespoke"),
    "ShubhAarambh.dc.html": ("ShubhAarambhPage", "/shubh-aarambh"),
    "Unboxed.dc.html": ("KivartKlicksPage", "/kivartklicks"),
}

# Small fixes to the design's logic where React behaves differently from the design runtime.
PATCHES = {
    "Main.dc.html": [
        # The load curtain plays once per browser session. The design marked it as seen in the
        # constructor, but React (Strict Mode) constructs a component twice, so the instance that
        # mounts always found it already seen. Mark it seen only once the curtain has played.
        (
            "window.sessionStorage.setItem('kvIntro', '1'); return true;",
            "return true;",
        ),
        (
            "if (kvIntro) setTimeout(() => { try { this.setState({ intro: false }); } catch (e) {} }, 1800);",
            "if (kvIntro) setTimeout(() => { try { window.sessionStorage.setItem('kvIntro', '1'); } catch (e) {} "
            "try { this.setState({ intro: false }); } catch (e) {} }, 1800);",
        ),
    ],
}

EXT = {}
for f in os.listdir(ASSETS):
    stem, ext = os.path.splitext(f)
    if re.fullmatch(r"[0-9a-f]{32}", stem):
        EXT[stem] = ext


def rewrite_assets(text):
    def blob(m):
        i = m.group(1)
        return "/assets/" + i + EXT.get(i, "")

    text = re.sub(r"/_blob/([0-9a-f]{32})", blob, text)
    text = text.replace("'/_blob/'", "'/assets/'").replace('"/_blob/"', '"/assets/"')

    # Bare ids concatenated onto a '/_blob/' prefix in the logic: add the extension.
    def bare(m):
        q, i = m.group(1), m.group(2)
        return q + i + EXT[i] + q if i in EXT else m.group(0)

    return re.sub(r"(['\"])([0-9a-f]{32})\1", bare, text)


def rewrite_href(h):
    m = re.fullmatch(r"([A-Za-z]+)\.dc\.html(#.*)?", h)
    if not m:
        return None
    route = PAGES[m.group(1) + ".dc.html"][1]
    return route + (m.group(2) or "")


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ATTR_MAP = {
    "class": "className", "for": "htmlFor", "tabindex": "tabIndex", "viewbox": "viewBox",
    "stroke-width": "strokeWidth", "stroke-linecap": "strokeLinecap", "stroke-linejoin": "strokeLinejoin",
    "fill-rule": "fillRule", "clip-rule": "clipRule", "stop-color": "stopColor", "autocomplete": "autoComplete",
    "maxlength": "maxLength", "inputmode": "inputMode", "playsinline": "playsInline", "autoplay": "autoPlay",
    "readonly": "readOnly", "srcset": "srcSet", "crossorigin": "crossOrigin", "colspan": "colSpan",
    "rowspan": "rowSpan", "preserveaspectratio": "preserveAspectRatio", "charset": "charSet",
    "onclick": "onClick", "onchange": "onChange", "oninput": "onInput", "onended": "onEnded",
    "onkeydown": "onKeyDown", "onsubmit": "onSubmit", "onfocus": "onFocus", "onblur": "onBlur",
    "onmouseenter": "onMouseEnter", "onmouseleave": "onMouseLeave", "onscroll": "onScroll", "onplay": "onPlay",
    "onpause": "onPause", "onload": "onLoad",
}
BOOL_ATTRS = {"muted", "playsinline", "autoplay", "loop", "controls", "required", "disabled", "checked",
              "hidden", "selected", "readonly", "multiple"}
HOLE = re.compile(r"\{\{\s*(.*?)\s*\}\}")


class Scope:
    def __init__(self):
        self.loops = []  # (as_name)

    def expr(self, path):
        path = path.strip()
        if re.fullmatch(r"true|false|null|-?\d+(\.\d+)?|'[^']*'|\"[^\"]*\"", path):
            return path
        parts = path.split(".")
        head = parts[0]
        if head == "$index" or head in self.loops:
            base = head
        else:
            base = "v." + head
        return base + "".join("?." + p for p in parts[1:])


def js_str(s):
    return json.dumps(s, ensure_ascii=False)


def interp(value, scope):
    """Attribute/text value with holes -> JS expression."""
    m = HOLE.fullmatch(value.strip()) if value else None
    if m and value.strip() == value.strip():
        if HOLE.fullmatch(value.strip()):
            return scope.expr(m.group(1)), True
    parts, last = [], 0
    for m in HOLE.finditer(value):
        parts.append(value[last:m.start()].replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${"))
        parts.append("${" + scope.expr(m.group(1)) + " ?? ''}")
        last = m.end()
    parts.append(value[last:].replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${"))
    return "`" + "".join(parts) + "`", False


def split_decls(css):
    out, depth, cur = [], 0, ""
    for ch in css:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [d for d in out if d.strip()]


def camel(prop):
    prop = prop.strip()
    if prop.startswith("--"):
        return js_str(prop)
    if prop.startswith("-"):
        prop = prop[1:]
        p = re.sub(r"-([a-z])", lambda m: m.group(1).upper(), prop)
        return p[0].upper() + p[1:]
    return re.sub(r"-([a-z])", lambda m: m.group(1).upper(), prop)


def style_expr(value, scope):
    if HOLE.search(value):
        e, _ = interp(value, scope)
        return "css(" + e + ")"
    items = []
    for d in split_decls(value):
        if ":" not in d:
            continue
        k, val = d.split(":", 1)
        items.append(camel(k) + ": " + js_str(val.strip()))
    return "{" + ", ".join(items) + "}"


class Compiler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.scope = Scope()
        self.in_xdc = False
        self.skip = 0  # inside <helmet>
        self.helmet = []
        self.depth = 0

    def emit(self, s):
        self.out.append(s)

    def attrs_jsx(self, tag, attrs):
        res = []
        for name, val in attrs:
            if name.startswith("hint-") or name in ("as",):
                continue
            jname = ATTR_MAP.get(name, name)
            if val is None:
                res.append(jname + "={true}" if name in BOOL_ATTRS else jname)
                continue
            if name == "style":
                res.append("style={" + style_expr(val, self.scope) + "}")
                continue
            if name == "href":
                r = rewrite_href(val)
                if r is not None:
                    val = r
            if HOLE.search(val):
                e, whole = interp(val, self.scope)
                res.append(jname + "={" + e + "}")
            elif name in BOOL_ATTRS and val in ("", name, "true"):
                res.append(jname + "={true}")
            else:
                res.append(jname + "=" + js_str(val))
        return (" " + " ".join(res)) if res else ""

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, selfclose=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, selfclose=True)

    def _start(self, tag, attrs, selfclose):
        if tag == "x-dc":
            self.in_xdc = True
            return
        if not self.in_xdc:
            return
        if tag == "helmet":
            self.skip += 1
            return
        if self.skip:
            self.helmet.append(self.get_starttag_text())
            return
        a = dict(attrs)
        if tag == "sc-if":
            e, _ = interp(a.get("value", ""), self.scope)
            self.emit("{(" + e + ") ? (<>")
            self.stack.append("sc-if")
            return
        if tag == "sc-for":
            e, _ = interp(a.get("list", ""), self.scope)
            name = a.get("as", "item")
            self.emit("{(" + e + " || []).map((" + name + ", $index) => (<React.Fragment key={$index}>")
            self.scope.loops.append(name)
            self.stack.append("sc-for")
            return
        jtag = tag
        href = a.get("href")
        if tag == "a" and href and rewrite_href(href) is not None:
            jtag = "Link"
        self.emit("<" + jtag + self.attrs_jsx(tag, attrs) + (" />" if (selfclose or tag in VOID) else ">"))
        if not (selfclose or tag in VOID):
            self.stack.append(jtag)

    def handle_endtag(self, tag):
        if tag == "x-dc":
            self.in_xdc = False
            return
        if not self.in_xdc:
            return
        if tag == "helmet":
            self.skip -= 1
            return
        if self.skip:
            self.helmet.append("</" + tag + ">")
            return
        if tag in VOID:
            return
        top = self.stack.pop()
        if top == "sc-if":
            self.emit("</>) : null}")
        elif top == "sc-for":
            self.scope.loops.pop()
            self.emit("</React.Fragment>))}")
        else:
            self.emit("</" + top + ">")

    def handle_data(self, data):
        if not self.in_xdc:
            return
        if self.skip:
            self.helmet.append(data)
            return
        if not data:
            return
        text = re.sub(r"\s+", " ", data)
        if text == " ":
            # whitespace between tags: keep one space unless it is pure indentation
            if "\n" in data:
                self.emit("{' '}" if self._inline_ctx() else "")
            else:
                self.emit("{' '}")
            return
        last = 0
        for m in HOLE.finditer(text):
            if m.start() > last:
                self.emit("{" + js_str(text[last:m.start()]) + "}")
            self.emit("{" + self.scope.expr(m.group(1)) + "}")
            last = m.end()
        if last < len(text):
            self.emit("{" + js_str(text[last:]) + "}")

    def _inline_ctx(self):
        # Whitespace with a newline between block-level siblings collapses to nothing visible;
        # keep it inside inline/text containers where it would render as a space.
        for t in reversed(self.stack):
            if t in ("sc-if", "sc-for"):
                continue
            return t in ("p", "span", "a", "Link", "strong", "em", "b", "i", "label", "button", "h1", "h2", "h3",
                         "h4", "li", "figcaption", "small", "option")
        return False


def port(fname, comp):
    src = open(os.path.join(DESIGN, fname), encoding="utf-8").read()
    src = rewrite_assets(src)
    title = re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip()
    helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S).group(1)
    css = "\n".join(re.findall(r"<style>(.*?)</style>", helmet, re.S)).strip()
    script = re.search(r"<script type=\"text/x-dc\"[^>]*>(.*?)</script>", src, re.S).group(1)
    c = Compiler()
    c.feed(src)
    c.close()
    if c.stack:
        sys.exit(f"{fname}: unclosed tags {c.stack[-5:]}")
    jsx = "".join(c.out)
    script = script.replace("class Component extends DCLogic", f"class {comp} extends DCLogic")
    for old, new in PATCHES.get(fname, []):
        if old not in script:
            sys.exit(f"{fname}: patch target not found: {old[:60]}")
        script = script.replace(old, new)
    body = f"""// @ts-nocheck
/* eslint-disable */
// Ported from design/{fname} by scripts/port_design.py ("{title}").
// The logic below is the design's own DCLogic class; render() is its template compiled to JSX.
"use client";

import React from "react";
import Link from "next/link";
import {{ DCLogic, css }} from "@/lib/dc";

const PAGE_CSS = {js_str(css)};
{script}
{comp}.prototype.render = function render() {{
  const v = this.renderVals();
  return (
    <>
      <style dangerouslySetInnerHTML={{{{ __html: PAGE_CSS }}}} />
      {jsx}
    </>
  );
}};

export default {comp};
"""
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, comp + ".tsx"), "w", encoding="utf-8") as fh:
        fh.write(body)
    return title


if __name__ == "__main__":
    titles = {}
    for f, (comp, route) in PAGES.items():
        titles[route] = port(f, comp)
        print("ported", f, "->", comp)
    with open(os.path.join(OUT, "titles.json"), "w", encoding="utf-8") as fh:
        json.dump(titles, fh, ensure_ascii=False, indent=2)
