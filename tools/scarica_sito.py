#!/usr/bin/env python3
"""Scarica contenuti e media di restauroecolore.com (WordPress + Enfold).

Uso:  python -I tools/scarica_sito.py sito-originale

Produce nella cartella di destinazione:
  api/        JSON grezzo dell'API REST (pagine, articoli, portfolio, media, tassonomie)
  html/       HTML renderizzato di ogni pagina
  media/      file originali a piena risoluzione (struttura anno/mese di WordPress)
  contenuti/  testo di ogni pagina in Markdown, con front matter
  INDICE.md, indice.json, media.json

Rilanciabile: salta cio' che e' gia' stato scaricato.
"""
import concurrent.futures as cf
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://www.restauroecolore.com"
API = BASE + "/wp-json/wp/v2"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
OUT = Path(sys.argv[1]).resolve()

TIPI = [("pagine", "pages"), ("articoli", "posts"), ("portfolio", "portfolio")]
TASSONOMIE = ["categories", "tags", "portfolio_entries"]

RE_UP = re.compile(r"""[^\s"'()<>,]*wp-content/uploads/[^\s"'()<>,\\?#]+""")
RE_EXT = re.compile(r"\.(jpe?g|png|gif|webp|svg|ico|pdf|mp4|webm|mov|docx?|zip)$", re.I)
RE_SIZE = re.compile(r"-\d+x\d+(\.\w+)$")


def fetch(url, tries=3):
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@~!$'()*[]")
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read(), r.headers
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404, 410):
                return None, None
            err = e
        except Exception as e:  # rete instabile: riprova
            err = e
        time.sleep(2 * (i + 1))
    print(f"  ERRORE {url}: {err}")
    return None, None


def api_all(rest):
    items, page = [], 1
    while True:
        body, hdr = fetch(f"{API}/{rest}?per_page=100&page={page}")
        if body is None:
            break
        items += json.loads(body)
        if page >= int(hdr.get("X-WP-TotalPages", 1)):
            break
        page += 1
    return items


def rel_di(url):
    """URL di un upload -> (percorso relativo a uploads/, URL assoluto) oppure None."""
    p = urllib.parse.urlsplit(urllib.parse.urljoin(BASE + "/", html.unescape(url)))
    if not p.netloc.endswith("restauroecolore.com") or "/wp-content/uploads/" not in p.path:
        return None
    rel = urllib.parse.unquote(p.path.split("/wp-content/uploads/", 1)[1])
    if not RE_EXT.search(rel):
        return None
    return rel, BASE + p.path


def locale(rel):
    parts = [re.sub(r'[<>:"|?*\\]', "_", x) for x in rel.split("/")]
    if any(x in ("", ".", "..") for x in parts):
        return None
    return Path("media", *parts)


def scarica(rel, url):
    loc = locale(rel)
    if loc is None:
        return False
    dst = OUT / loc
    if dst.exists() and dst.stat().st_size > 0:
        return True
    body, _ = fetch(url)
    if not body:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    tmp.write_bytes(body)
    tmp.replace(dst)
    return True


def risolvi(rel, url):
    """Per un file trovato nell'HTML: prova l'originale, poi la miniatura cosi' com'e'."""
    norm = RE_SIZE.sub(r"\1", rel)
    if norm != rel:
        nurl = url.rsplit("/", 1)[0] + "/" + urllib.parse.quote(norm.rsplit("/", 1)[-1])
        if scarica(norm, nurl):
            return norm
    return rel if scarica(rel, url) else None


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP = {"script", "style", "noscript", "svg", "template"}
BLOCK = {"p", "div", "section", "article", "ul", "ol", "table", "blockquote", "header", "footer", "main",
         "form", "figure", "figcaption", "nav", "aside", "dl", "dt", "dd", "address", "pre", "hr", "tbody", "thead"}
HEAD = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
REGIONI = {"header": "header", "main": "main", "footer": "footer", "socket": "footer"}


class Estrattore(HTMLParser):
    """HTML Enfold -> Markdown grezzo, separato per regione (header / main / footer / sidebar)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, regione, skip, href)
        self.out = {"header": [], "main": [], "footer": [], "sidebar": [], None: []}
        self.media = []
        self.skip = 0
        self.lists = 0

    def regione(self):
        for t in reversed(self.stack):
            if t[1]:
                return t[1]
        return None

    def emit(self, s):
        self.out[self.regione()].append(s)

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag not in VOID:
            reg = REGIONI.get(a.get("id", "")) or ("sidebar" if tag == "aside" else None)
            skip = tag in SKIP
            self.skip += skip
            href = a.get("href") if tag == "a" and a.get("href") else None
            self.stack.append((tag, reg, skip, href))
        if self.skip:
            return
        if self.regione() == "main":
            for v in a.values():
                self.media += RE_UP.findall(v)
        if tag in HEAD:
            self.emit("\n\n" + "#" * HEAD[tag] + " ")
        elif tag == "li":
            self.emit("\n" + "  " * max(self.lists - 1, 0) + "- ")
        elif tag in ("br", "tr"):
            self.emit("\n")
        elif tag == "a":
            if a.get("href"):
                self.emit("[")
        elif tag == "img":
            src = a.get("data-src") or a.get("src", "")
            if src and not src.startswith("data:"):
                self.emit(f"![{a.get('alt', '').strip()}]({src})")
        elif tag == "iframe":
            self.emit(f"\n\n[iframe]({a.get('src') or a.get('data-src', '')})\n\n")
        elif tag in ("input", "textarea", "select"):
            if a.get("type") not in ("hidden", "submit"):
                self.emit(f"\n- campo: {tag} {a.get('type', '')} name={a.get('name', '')} {a.get('placeholder', '')}")
            elif a.get("type") == "submit":
                self.emit(f"\n- pulsante: {a.get('value', '')}")
        elif tag in ("strong", "b"):
            self.emit("**")
        elif tag in BLOCK:
            if tag in ("ul", "ol"):
                self.lists += 1
            self.emit("\n\n")

    def chiudi(self, tag, href):
        if tag in HEAD or tag in BLOCK:
            if tag in ("ul", "ol"):
                self.lists = max(self.lists - 1, 0)
            self.emit("\n\n")
        elif tag == "li":
            self.emit("\n")
        elif tag == "a":
            if href:
                self.emit(f"]({href})")
        elif tag in ("strong", "b"):
            self.emit("**")
        elif tag in ("td", "th"):
            self.emit(" | ")

    def handle_endtag(self, tag):
        idx = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if idx is None:
            return
        while len(self.stack) > idx:
            t, _, skip, href = self.stack[-1]
            if not self.skip:
                self.chiudi(t, href)
            self.stack.pop()
            self.skip -= skip

    def handle_data(self, data):
        if not self.skip:
            self.emit(re.sub(r"\s+", " ", data))


def pulisci(chunks):
    t = "".join(chunks)
    t = re.sub(r"(?<!!)\[\s*\]\([^)]*\)", "", t)
    t = re.sub(r"\*\*\s*\*\*", "", t)
    righe = []
    for l in t.split("\n"):
        ind = len(l) - len(l.lstrip(" ")) if l.lstrip(" ").startswith("- ") else 0
        righe.append(" " * ind + re.sub(r"[ \t\xa0]+", " ", l).strip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(righe)).strip() + "\n"


def nome_file(tipo, item):
    if tipo == "pagine":
        path = urllib.parse.unquote(urllib.parse.urlsplit(item["link"]).path).strip("/")
        nome = path.replace("/", "--") or "home"
    else:
        nome = urllib.parse.unquote(item["slug"])
    return re.sub(r'[<>:"|?*\\/]', "_", nome)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for d in ("api", "html", "media", "contenuti"):
        (OUT / d).mkdir(parents=True, exist_ok=True)

    # 1. API REST
    print("1/5 API REST...")
    dati = {}
    for rest in [r for _, r in TIPI] + TASSONOMIE + ["media"]:
        dati[rest] = api_all(rest)
        (OUT / "api" / f"{rest}.json").write_text(json.dumps(dati[rest], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {rest}: {len(dati[rest])}")
    termini = {t["id"]: html.unescape(t["name"]) for tax in TASSONOMIE for t in dati[tax]}

    voci = []
    for tipo, rest in TIPI:
        for it in dati[rest]:
            voci.append({"tipo": tipo, "item": it, "nome": nome_file(tipo, it)})
    if not any(v["tipo"] == "pagine" and v["nome"] == "home" for v in voci):
        voci.append({"tipo": "pagine", "nome": "home",
                     "item": {"id": 0, "slug": "home", "link": BASE + "/", "title": {"rendered": "Home"}}})

    # 2. HTML renderizzato
    print(f"2/5 HTML di {len(voci)} pagine...")

    def prendi_html(v):
        dst = OUT / "html" / v["tipo"] / (v["nome"] + ".html")
        if not (dst.exists() and dst.stat().st_size > 0):
            body, _ = fetch(v["item"]["link"])
            if not body:
                return False
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(body)
        v["html"] = dst
        return True

    with cf.ThreadPoolExecutor(6) as ex:
        ok = list(ex.map(prendi_html, voci))
    falliti_html = [v["item"]["link"] for v, o in zip(voci, ok) if not o]

    # 3. Parsing
    print("3/5 Estrazione testi...")
    trovati = {}  # rel -> url (solo file citati nel contenuto principale)
    globale = None
    for v in voci:
        if "html" not in v:
            continue
        p = Estrattore()
        p.feed(v["html"].read_text(encoding="utf-8", errors="replace"))
        v["md"] = pulisci(p.out["main"])
        v["rels"] = []
        for u in p.media + RE_UP.findall(v["md"]):
            r = rel_di(u)
            if r:
                trovati.setdefault(r[0], r[1])
                if r[0] not in v["rels"]:
                    v["rels"].append(r[0])
        if v["nome"] == "home" and v["tipo"] == "pagine":
            globale = p
            for chunk in p.out["header"] + p.out["footer"]:
                for u in RE_UP.findall(chunk):
                    r = rel_di(u)
                    if r:
                        trovati.setdefault(r[0], r[1])

    # 4. Media
    libreria = {}  # rel -> voce media
    for m in dati["media"]:
        r = rel_di(m.get("source_url", ""))
        if r:
            libreria[r[0]] = (m, r[1])
    print(f"4/5 Media: {len(libreria)} in libreria, {len(trovati)} citati nelle pagine...")
    with cf.ThreadPoolExecutor(8) as ex:
        esiti = list(ex.map(lambda kv: scarica(kv[0], kv[1][1]), libreria.items()))
    falliti_media = [rel for rel, o in zip(libreria, esiti) if not o]
    mappa = {rel: rel for rel, o in zip(libreria, esiti) if o}
    extra = [(rel, url) for rel, url in trovati.items() if RE_SIZE.sub(r"\1", rel) not in mappa and rel not in mappa]
    with cf.ThreadPoolExecutor(8) as ex:
        ris = list(ex.map(lambda x: risolvi(*x), extra))
    for (rel, _), fin in zip(extra, ris):
        if fin:
            mappa[rel] = fin
        else:
            falliti_media.append(rel)
    for rel in trovati:
        mappa.setdefault(rel, mappa.get(RE_SIZE.sub(r"\1", rel)))

    def loc_di(rel):
        fin = mappa.get(rel)
        return locale(fin).as_posix() if fin else None

    def riscrivi(md, prefisso):
        def sub(m):
            r = rel_di(m.group(0))
            loc = r and loc_di(r[0])
            return prefisso + loc.replace(" ", "%20") if loc else m.group(0)
        return RE_UP.sub(sub, md)

    # 5. Markdown + indici
    print("5/5 Markdown e indici...")
    per_id = {m["id"]: rel for rel, (m, _) in libreria.items()}
    slug_di = {it["id"]: it["slug"] for _, rest in TIPI for it in dati[rest]}
    usato_in = {}
    indice = []
    for v in voci:
        if "md" not in v:
            continue
        it = v["item"]
        titolo = html.unescape(it.get("title", {}).get("rendered", ""))
        imgs = [l for l in (loc_di(r) for r in v["rels"]) if l]
        imgs = list(dict.fromkeys(imgs))
        cop = per_id.get(it.get("featured_media") or 0)
        cop = loc_di(cop) if cop else None
        tags = [termini[i] for k in ("categories", "tags", "portfolio_entries") for i in it.get(k, []) if i in termini]
        rel_md = f"contenuti/{v['tipo']}/{v['nome']}.md"
        for l in imgs + ([cop] if cop else []):
            usato_in.setdefault(l, [])
            if rel_md not in usato_in[l]:
                usato_in[l].append(rel_md)
        fm = ["---", f"titolo: {json.dumps(titolo, ensure_ascii=False)}", f"url: {it['link']}",
              f"tipo: {v['tipo']}", f"id: {it['id']}"]
        if it.get("date"):
            fm.append(f"data: {it['date'][:10]}")
        if it.get("parent"):
            fm.append(f"genitore: {slug_di.get(it['parent'], it['parent'])}")
        if tags:
            fm.append(f"termini: {json.dumps(tags, ensure_ascii=False)}")
        if cop:
            fm.append(f"copertina: {cop}")
        if imgs:
            fm.append("immagini:")
            fm += [f"  - {l}" for l in imgs]
        fm.append("---\n")
        dst = OUT / rel_md
        dst.parent.mkdir(parents=True, exist_ok=True)
        corpo = riscrivi(v["md"], "../../")
        dst.write_text("\n".join(fm) + "\n" + corpo, encoding="utf-8")
        parole = len(re.findall(r"\w+", re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", v["md"])))
        indice.append({"tipo": v["tipo"], "id": it["id"], "titolo": titolo, "url": it["link"], "slug": it.get("slug"),
                       "genitore": slug_di.get(it.get("parent") or 0), "data": (it.get("date") or "")[:10],
                       "termini": tags, "copertina": cop, "immagini": imgs, "parole": parole, "md": rel_md,
                       "html": f"html/{v['tipo']}/{v['nome']}.html"})

    if globale:
        g = "# Header (menu)\n\n" + pulisci(globale.out["header"]) + "\n# Footer\n\n" + pulisci(globale.out["footer"])
        g += "\n# Sidebar (home)\n\n" + pulisci(globale.out["sidebar"])
        (OUT / "contenuti" / "_globale.md").write_text(riscrivi(g, "../"), encoding="utf-8")

    media = []
    for rel, (m, _) in libreria.items():
        loc = loc_di(rel)
        det = m.get("media_details") or {}
        media.append({"id": m["id"], "file": loc, "titolo": html.unescape(m.get("title", {}).get("rendered", "")),
                      "alt": m.get("alt_text", ""),
                      "didascalia": re.sub(r"<[^>]+>", "", html.unescape(m.get("caption", {}).get("rendered", ""))).strip(),
                      "mime": m.get("mime_type"), "larghezza": det.get("width"), "altezza": det.get("height"),
                      "allegato_a": slug_di.get(m.get("post") or 0), "usato_in": usato_in.get(loc, [])})
    in_lib = {x["file"] for x in media}
    for rel in sorted(set(mappa.values()) - {None}):
        loc = locale(rel).as_posix()
        if loc not in in_lib:
            in_lib.add(loc)
            media.append({"id": None, "file": loc, "titolo": "", "alt": "", "didascalia": "", "mime": None,
                          "larghezza": None, "altezza": None, "allegato_a": None, "usato_in": usato_in.get(loc, [])})
    (OUT / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "media.json").write_text(json.dumps(media, ensure_ascii=False, indent=1), encoding="utf-8")

    righe = ["# Indice sito originale restauroecolore.com\n"]
    for tipo, _ in TIPI:
        gruppo = sorted((x for x in indice if x["tipo"] == tipo), key=lambda x: x["url"])
        righe.append(f"\n## {tipo} ({len(gruppo)})\n")
        for x in gruppo:
            path = urllib.parse.unquote(urllib.parse.urlsplit(x["url"]).path)
            t = f" — {', '.join(x['termini'])}" if x["termini"] else ""
            righe.append(f"- [{x['titolo'] or '(senza titolo)'}]({x['md']}) `{path}` — {x['parole']} parole, {len(x['immagini'])} img{t}")
    (OUT / "INDICE.md").write_text("\n".join(righe) + "\n", encoding="utf-8")

    files = [f for f in (OUT / "media").rglob("*") if f.is_file()]
    print("\n=== RIEPILOGO ===")
    for tipo, _ in TIPI:
        print(f"{tipo}: {sum(1 for x in indice if x['tipo'] == tipo)}")
    print(f"media scaricati: {len(files)} file, {sum(f.stat().st_size for f in files) / 1e6:.1f} MB")
    print(f"media non usati in nessuna pagina: {sum(1 for x in media if not x['usato_in'])}")
    print(f"HTML falliti: {len(falliti_html)} {falliti_html[:10]}")
    print(f"media falliti: {len(falliti_media)} {falliti_media[:20]}")


if __name__ == "__main__":
    main()
