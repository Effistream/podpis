#!/usr/bin/env python3
"""Vyrobí fotku do podpisu v2: portrait-<jmeno>-v2-pole@2x.jpg (144×144, JPG q85, sRGB).

Použití (z kořene repozitáře):
  python3 sablony/foto.py ~/Desktop/tom.jpg portrait-tom
  python3 sablony/foto.py ~/Desktop/tom.jpg portrait-tom --bez-toningu

Vstup musí být čtverec (min. 600×600) s obličejem vycentrovaným vodorovně, temenem těsně pod
horní hranou a bradou ve spodní třetině. Ořez udělej předem (viz README), skript neořezává.

Výchozí režim vyrenderuje sablony/v2-pole/portrait.html v Chromiu (Playwright) se stejným
tónováním jako Danielova fotka. Potřebuje: pip install playwright && playwright install chromium
--bez-toningu jen zmenší fotku přes ImageMagick (magick). Je to záložní varianta bez tónování.

Výstup se uloží do kořene repozitáře. Commitni jen ten JPG, zdrojovou fotku necommituj.
"""
import argparse, asyncio, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TPL = REPO / "sablony" / "v2-pole" / "portrait.html"


def check_source(src: Path):
    try:
        out = subprocess.run(["magick", "identify", "-format", "%w %h", str(src)],
                             capture_output=True, text=True, check=True).stdout.split()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("upozornění: rozměr zdroje neověřen (chybí ImageMagick), zkontroluj čtverec ručně")
        return
    w, h = int(out[0]), int(out[1])
    if w != h:
        sys.exit(f"zdroj má {w}×{h}, musí být čtverec – nejdřív ho ořízni (README, krok 2)")
    if w < 600:
        print(f"upozornění: zdroj má jen {w}×{h}, doporučeno aspoň 600×600")


async def render(src: Path, out: Path):
    from playwright.async_api import async_playwright
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(src, tmp / "zdroj.jpg")
        (tmp / "portrait.html").write_text(TPL.read_text(encoding="utf-8").replace("{{SRC}}", "zdroj.jpg"),
                                           encoding="utf-8")
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 400, "height": 400}, device_scale_factor=2)
            await pg.goto((tmp / "portrait.html").as_uri())
            await pg.evaluate("() => (window.ready || Promise.resolve())")
            el = await pg.query_selector("#stage")
            await el.screenshot(path=str(out), type="jpeg", quality=85)
            await b.close()


def plain(src: Path, out: Path):
    subprocess.run(["magick", str(src), "-colorspace", "sRGB", "-resize", "144x144^", "-gravity", "center",
                    "-extent", "144x144", "-strip", "-quality", "85", str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zdroj", type=Path, help="čtvercová zdrojová fotka (JPG/PNG)")
    ap.add_argument("prefix", help="např. portrait-tom (malá písmena, bez diakritiky)")
    ap.add_argument("--bez-toningu", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"portrait-[a-z0-9-]+", a.prefix):
        sys.exit("prefix musí mít tvar portrait-<jmeno>, malá písmena bez diakritiky, např. portrait-tom")
    if not a.zdroj.exists():
        sys.exit(f"soubor {a.zdroj} neexistuje")
    out = REPO / f"{a.prefix}-v2-pole@2x.jpg"
    if out.exists():
        sys.exit(f"{out.name} už v repu je. Nepřepisuj ho, odkazují na něj odeslané e-maily. "
                 "Novou verzi ulož pod jiným prefixem, např. portrait-tom2.")
    check_source(a.zdroj)
    if a.bez_toningu:
        plain(a.zdroj, out)
    else:
        asyncio.run(render(a.zdroj, out))
    print(f"{out.name}: {out.stat().st_size / 1024:.1f} KB – prohlédni ho zvětšený, než ho commitneš")


if __name__ == "__main__":
    main()
