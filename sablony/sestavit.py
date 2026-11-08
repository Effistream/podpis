#!/usr/bin/env python3
"""Sestaví podpis v2 s tvými údaji do HTML stránky, ze které ho zkopíruješ do Gmailu.

Použití (z kořene repozitáře):
  python3 sablony/sestavit.py --jmeno "Tomáš Novák" --role "Obchodní manažer" \\
      --telefon "+420 777 123 456" --email tomas.novak@effistream.eu --foto portrait-tom

Výstup: podpis-<foto>.html v kořeni repa (je v .gitignore, necommituj ho). Otevři ho v prohlížeči,
označ podpis myší, Cmd+C (Ctrl+C) a vlož do Gmailu. Gmail neumí vložit HTML zdroják, jen vykreslený podpis.
Skript ověří, že fotka už je veřejně na GitHub Pages (jinak by se v Gmailu ukázal rozbitý obrázek).
Jen standardní knihovna Pythonu 3.
"""
import argparse, html, re, sys, unicodedata, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TPL = REPO / "sablony" / "v2-pole"
ASSET_BASE = "https://effistream.github.io/podpis/"
GMAIL_LIMIT = 10_000


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def fill(tpl, values):
    out = tpl
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", out)
    if left:
        sys.exit(f"nedoplněné placeholdery: {sorted(set(left))}")
    return re.sub(r"<!--.*?-->", "", out, flags=re.S).strip()


def online(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "podpis-sestavit"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jmeno", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--telefon", required=True, help='čitelný tvar, např. "+420 777 123 456"')
    ap.add_argument("--email", required=True)
    ap.add_argument("--foto", required=True, help="prefix fotky, např. portrait-tom")
    ap.add_argument("--bez-kontroly", action="store_true", help="neověřovat fotku na Pages (offline)")
    a = ap.parse_args()

    e164 = re.sub(r"[^\d+]", "", a.telefon)
    if not re.fullmatch(r"\+\d{9,15}", e164):
        sys.exit(f"telefon {a.telefon!r} musí být s předvolbou, např. +420 777 123 456")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", a.email):
        sys.exit(f"e-mail {a.email!r} nevypadá platně")

    photo_url = f"{ASSET_BASE}{a.foto}-v2-pole@2x.jpg"
    if not a.bez_kontroly and not online(photo_url):
        sys.exit(f"fotka {photo_url} zatím není online. Commitni a pushni ji (README, krok 4), "
                 "počkej asi minutu na GitHub Pages a spusť znovu.")

    values = {"ASSET_BASE": ASSET_BASE, "NAME": html.escape(a.jmeno), "ROLE": html.escape(a.role),
              "PHONE": html.escape(a.telefon), "PHONE_E164": e164, "EMAIL": html.escape(a.email),
              "PHOTO": a.foto, "UTM_CAMPAIGN": slug(a.jmeno)}
    sig = fill((TPL / "signature.html").read_text(encoding="utf-8"), values)
    rep = fill((TPL / "reply.html").read_text(encoding="utf-8"), values)
    for name, s in (("podpis", sig), ("odpověď", rep)):
        if len(s) > GMAIL_LIMIT:
            sys.exit(f"{name} má {len(s)} znaků, Gmail bere max {GMAIL_LIMIT} – zkrať roli")

    page = f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8"><title>Podpis {html.escape(a.jmeno)}</title>
<style>body{{font:15px/1.5 -apple-system,Helvetica,Arial,sans-serif;max-width:640px;margin:40px auto;padding:0 16px;color:#222}}
h2{{font-size:16px;margin:40px 0 8px}} .box{{border:1px dashed #bbb;padding:24px;background:#fff}} ol{{padding-left:20px}}</style>
</head><body>
<h1 style="font-size:20px">Podpis {html.escape(a.jmeno)} – varianta v2</h1>
<ol>
<li>Označ myší celý obsah rámečku (od fotky po právní řádek) a zkopíruj (Cmd+C / Ctrl+C).</li>
<li>Gmail → ozubené kolo → Zobrazit všechna nastavení → Obecné → Podpis → Vytvořit nový → vložit (Cmd+V).</li>
<li>Totéž udělej s odpovědí jako druhým podpisem.</li>
<li>Pod editorem nastav „Pro nové e-maily“ = podpis, „Při odpovědi/přeposílání“ = odpověď. Dole Uložit změny.</li>
</ol>
<h2>1. Podpis pro nové e-maily</h2>
<div class="box">{sig}</div>
<h2>2. Odpověď (kratší, pro odpovědi a přeposílání)</h2>
<div class="box">{rep}</div>
</body></html>
"""
    out = REPO / f"podpis-{a.foto}.html"
    out.write_text(page, encoding="utf-8")
    print(f"hotovo: {out}  (podpis {len(sig)} znaků, odpověď {len(rep)} znaků)")


if __name__ == "__main__":
    main()
