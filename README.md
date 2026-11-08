# podpis

Obrázky do e-mailových podpisů EffiStream, servírované přes GitHub Pages:
`https://effistream.github.io/podpis/<soubor>`

**Není to web ani aplikace.** Nic se tu nepřihlašuje a kořen `https://effistream.github.io/podpis/`
vrací 404, protože tu není úvodní stránka. To je v pořádku. Funguje jen přímý odkaz na konkrétní soubor.

> **Nemazat, nepřejmenovávat, nepřepisovat.** Na soubory v kořeni odkazují už odeslané e-maily.
> Přepsání souboru pod stejným jménem změní obrázek i ve starých mailech (po vypršení cache Gmailu).
> Nová verze = nový název souboru.

Zatím je tu jen varianta **v2 (Vektorové pole)**: fotka, jméno a kontakty, pod tím klikací animovaný banner effistream.eu.

---

## Návod: podpis pro dalšího člena týmu

Píšu ho pro AI agenta (Claude Code apod.), kterému kolega řekne „nastav mi e-mailový podpis EffiStream“.
Člověk ho přečte taky. Kroky 1–5 dělá agent, krok 6 (vložení do Gmailu) musí udělat člověk sám.

### Co potřebuješ od člověka

| Údaj | Příklad | Poznámka |
|---|---|---|
| Jméno a příjmení | `Tomáš Novák` | s diakritikou, jak se má zobrazit |
| Role | `Obchodní manažer` | krátce, ideálně do ~35 znaků (vejde se na řádek vedle fotky) |
| Telefon | `+420 777 123 456` | s předvolbou, mezery po trojicích |
| E-mail | `tomas.novak@effistream.eu` | firemní adresa |
| Fotka | soubor JPG/PNG | portrét, ideálně ≥ 600 px na kratší straně, ostrý, obličej zepředu |

Na nic z toho se neptej, pokud to už víš z kontextu. Fotku si ale vždycky vyžádej jako soubor.

### Prostředí

- `git` s právem push do `Effistream/podpis` (stačí člen organizace Effistream na GitHubu)
- Python 3
- Pro fotku s tónováním: `pip install playwright && playwright install chromium`
- Pro ořez a kontrolu rozměrů: ImageMagick (`magick`, na Macu `brew install imagemagick`)

### Krok 1: Klon a prefix

```bash
git clone https://github.com/Effistream/podpis.git && cd podpis
git pull   # vždy začni z aktuálního main
```

Zvol prefix fotky `portrait-<jmeno>`: malá písmena, bez diakritiky, bez mezer, např. `portrait-tom`.
Musí být unikátní. Zkontroluj, že `portrait-<jmeno>-v2-pole@2x.jpg` v repu ještě není.
Když už existuje (nová fotka téhož člověka), použij `portrait-tom2` apod. Nikdy nepřepisuj.

### Krok 2: Ořez zdrojové fotky

Cíl je **čtverec** (doporučeno 600×600 px nebo víc), který nikam necommituješ. Ulož ho mimo repo.

Kompozice musí sedět s Danielovou fotkou (`portrait-daniel-v2-pole@2x.jpg`, otevři si ji pro srovnání):
- obličej vodorovně uprostřed,
- temeno hlavy těsně pod horní hranou (nebo lehce useknuté),
- brada zhruba na hranici spodní třetiny, vidět je krk a kousek ramen,
- žádné zaoblení, rámeček ani průhlednost.

Příklad ořezu přes ImageMagick (čísla dopočítej podle fotky, `W` = šířka čtverce, `X`,`Y` = levý horní roh):

```bash
magick tom.jpg -crop WxW+X+Y +repage -resize 600x600 ~/tom-ctverec.jpg
```

Výsledek si prohlédni (otevři obrázek) a porovnej s Danielovou fotkou. Když obličej nesedí, ořízni znovu.

### Krok 3: Výroba fotky do podpisu

```bash
python3 sablony/foto.py ~/tom-ctverec.jpg portrait-tom
```

Výstup `portrait-tom-v2-pole@2x.jpg` v kořeni repa musí splňovat:

| Parametr | Hodnota |
|---|---|
| Rozměr souboru | **144 × 144 px** (podpis ho zobrazí jako 72 × 72, 2× kvůli retině) |
| Formát | JPG, kvalita 85, sRGB |
| Velikost | do ~15 kB (Danielova má 6 kB) |
| Tvar | čtverec, ostré rohy |
| Název | `portrait-<jmeno>-v2-pole@2x.jpg` (přípona `-v2-pole@2x.jpg` je povinná, šablona ji skládá z prefixu) |

Skript dělá totéž co u Daniela: obličej nechá v původních barvách a pozadí za ním odbarví a lehce ochladí,
aby ladilo s šedomodrým bannerem. Když Playwright nejde nainstalovat, použij `--bez-toningu`
(jen zmenšení přes ImageMagick). Vypadá to o něco hůř, ale funguje to.

**Výsledek si vždy prohlédni zvětšený.** Obličej má být uvnitř oválu, který zůstal barevný.
Když je obličej mimo střed (barevný ovál je vedle obličeje, nebo je obličej šedivý), vrať se ke kroku 2 a ořízni jinak.
Smaž nepovedený JPG a zkus to znovu.

### Krok 4: Commit a push fotky

```bash
git add portrait-tom-v2-pole@2x.jpg
git commit -m "Fotka do podpisu: Tomáš Novák (v2)"
git push
```

Commituj **jen ten jeden JPG**. Zdrojovou fotku, `podpis-*.html` ani nic jiného ne.
Nic stávajícího neměň. GitHub Pages fotku zveřejní asi do minuty. Ověř:

```bash
curl -sI https://effistream.github.io/podpis/portrait-tom-v2-pole@2x.jpg | head -1   # čekej HTTP 200
```

### Krok 5: Sestavení podpisu

```bash
python3 sablony/sestavit.py --jmeno "Tomáš Novák" --role "Obchodní manažer" \
  --telefon "+420 777 123 456" --email tomas.novak@effistream.eu --foto portrait-tom
```

Skript doplní údaje do šablon `sablony/v2-pole/signature.html` (nový e-mail) a `reply.html` (odpověď),
ověří, že fotka je online, a zapíše `podpis-portrait-tom.html` (je v `.gitignore`).
Otevři ho člověku v prohlížeči (`open podpis-portrait-tom.html`) a ukaž mu ho. Měl by zkontrolovat údaje.

### Krok 6: Vložení do Gmailu (dělá člověk)

Agent tohle za člověka neudělá: Gmail neumí vložit HTML zdroják, jen vykreslený podpis zkopírovaný z prohlížeče.
Předej mu tento postup:

1. V otevřené stránce označ myší celý první rámeček (od fotky po právní řádek) a zkopíruj ho (Cmd+C).
2. Gmail → ozubené kolo → **Zobrazit všechna nastavení** → **Obecné** → **Podpis** → **Vytvořit nový**
   (název např. „EffiStream“) → vlož (Cmd+V).
3. Totéž s druhým rámečkem (odpověď) jako druhý podpis („EffiStream odpověď“).
4. Pod editorem v **Výchozí nastavení podpisu** dej „Pro nové e-maily“ = EffiStream a „Při odpovědi/přeposílání“
   = EffiStream odpověď. Úplně dole **Uložit změny**.
5. Pošli si testovací e-mail a otevři ho i v mobilu. Fotka i banner se musí načíst.

Když se v Gmailu místo fotky ukáže rozbitý obrázek, fotka ještě není na Pages (krok 4) nebo nesedí prefix.

---

## Struktura repa

| Cesta | Co to je |
|---|---|
| `*.jpg`, `*.png`, `*.gif` v kořeni | Veřejné obrázky, na které odkazují podpisy. Neměnit. |
| `sablony/v2-pole/signature.html`, `reply.html` | HTML šablony podpisu s placeholdery `{{NAME}}`, `{{ROLE}}`, `{{PHONE}}`, `{{PHONE_E164}}`, `{{EMAIL}}`, `{{PHOTO}}`, `{{ASSET_BASE}}`, `{{UTM_CAMPAIGN}}` |
| `sablony/v2-pole/portrait.html` | Předloha ořezu a tónování fotky (používá `foto.py`) |
| `sablony/foto.py` | Výroba fotky 144×144 |
| `sablony/sestavit.py` | Doplnění údajů a stránka ke zkopírování do Gmailu |

Šablony neupravuj. Kdo chce jiný podpis (jiná grafika, další varianta), ať se ozve Danielovi.
Zdroj grafiky, ostatní varianty a technická pravidla (limit Gmailu 10 000 znaků, dark mode, Outlook)
jsou v interní knowledge base: `effistream.knowledge/email-podpisy`.
