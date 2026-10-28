"""Step 5 — contact sheets for visual review + check that no visible text lies outside the paper.

Writes PNGs to 05_交付紀錄/qa/. Look at them (and zoom into doubtful pages at 300 dpi) before
telling anyone the package is fine — a passing script is not a visual check.
"""
import json

import pymupdf as f
from PIL import Image, ImageDraw

from .common import Project, jload


def main():
    P = Project.load()
    pkg = P.get("package_name", "{name}_施工圖與零件圖分冊").format(name=P.name)
    D = P.pending / pkg
    qa = P.records / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    out = []
    for book in sorted(D.glob("*圖冊.pdf")):
        d = f.open(book)
        for idx, p in enumerate(d):
            spans = [s for b in p.get_text("dict")["blocks"] if "lines" in b for ln in b["lines"] for s in ln["spans"] if s["text"].strip()]
            assert spans, (book.name, idx, "no text")
            bad = [(s["text"], s["bbox"]) for s in spans if s["bbox"][0] < -.5 or s["bbox"][1] < -.5
                   or s["bbox"][2] > p.rect.width + .5 or s["bbox"][3] > p.rect.height + .5]
            assert not bad, (book.name, idx, bad)
        sheets = []
        for start in range(0, len(d), 8):
            c = Image.new("RGB", (1800, 2720), "white")
            dr = ImageDraw.Draw(c)
            for idx in range(start, min(start + 8, len(d))):
                pix = d[idx].get_pixmap(matrix=f.Matrix(.74, .74))
                im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                i = idx - start
                x, y = i % 2 * 900, i // 2 * 680
                c.paste(im, (x, y + 25))
                dr.text((x + 10, y + 5), f"{idx + 1} / {len(d)}", fill="black")
            fn = qa / f"{book.stem}_contact_{start // 8 + 1}.png"
            c.save(fn)
            sheets.append(str(fn))
        out.append({"book": book.name, "pages": len(d), "contact_sheets": sheets})
        print(book.name, len(d), *sheets, sep="\n  ")
        d.close()
    (qa / "page_checks.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
