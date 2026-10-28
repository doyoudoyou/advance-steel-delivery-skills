"""Step 4 — assemble the package in 03_待確認交付 (never 04_正式交付; that needs the user's confirmation).

* copies every verified DWG, merges per-DWG PDFs, builds the construction book and the parts book
* pixel-compares every book page with its single-sheet source PDF
* checks the drawing list pages contain each number/title exactly once and no parts
* writes 交付說明.txt (generated from facts — edit `notes_extra` in the config for project-specific lines),
  a source/number CSV, a manifest JSON, the ZIP, and reads the ZIP back member by member.

Re-run: delete the target folder + ZIP in 03_待確認交付 first (the script refuses to overwrite).
"""
import csv
import hashlib
import shutil
import zipfile
from pathlib import Path

import pymupdf as f

from .common import CATS, Project, jdump, jload, sha


def main():
    P = Project.load()
    W = P.work
    name = P.name
    excluded = P.get("excluded", {})
    J = [j for j in jload(W / "jobs.json") if j["key"] not in excluded]
    R = jload(W / "construction_index.json")
    OFF = jload(W / "offsheet_warnings.json")
    REVR = jload(W / "revision_removed.json")
    pkg = P.get("package_name", "{name}_施工圖與零件圖分冊").format(name=name)
    D = P.pending / pkg
    archive = P.pending / (pkg + P.get("zip_suffix", "_交付包") + ".zip")
    assert not D.exists() and not archive.exists(), ("target exists; clear it before re-running", str(D))
    D.mkdir(parents=True)
    forbid = [n for n in P.get("forbidden_texts", []) if n != name]
    must = P.get("required_texts", [])
    folders = {CATS["cover"]: "00_封面與圖號", CATS["index"]: "00_封面與圖號", **P.get("folders", {})}

    received = {}
    for line in (P.records / f"received-{P['batch']}-sha256.txt").read_text(encoding="utf-8").splitlines():
        h, n = line.split(None, 1)
        received[n.lstrip("*")] = h
    resolved, edge_flags = [], []
    for j in J:
        w = W / "production" / j["key"]
        q = jload(w / "qc.json")
        assert q["success"] and q["native_reopened"], j["key"]
        src, dwg = Path(j["source"]), Path(j["output"])
        assert sha(src) == j["source_sha256"] and sha(dwg) == q["dwg_sha256"], j["key"]
        if src.parent == P.source_dir:
            assert received[src.name] == j["source_sha256"], (j["key"], "differs from received hash list")
        folder = D / folders.get(j["category"], j["category"])
        folder.mkdir(exist_ok=True)
        target = folder / dwg.name
        assert not target.exists(), ("duplicate output name", str(target))
        shutil.copy2(dwg, target)
        merged = f.open()
        for i, p in enumerate(q["pdfs"]):
            assert sha(p) == q["pdf_sha256"][i]
            doc = f.open(p)
            assert len(doc) == 1
            page = doc[0]
            text = page.get_text()
            assert text.strip(), (j["key"], "blank PDF page")
            pg = j["pages"][i]
            if j["mode"] in ("apply", "index"):
                assert pg["Number"] in text and name in text, (j["key"], text[:200])
                assert all(t in text for t in must), (j["key"], "required text missing", must)
                assert "REVISIONS" not in text.upper(), (j["key"], "old revision table printed")
            if j["mode"] == "cover":
                assert name in text
            if j["mode"] in ("apply", "index", "cover"):
                assert not any(n in text for n in forbid), (j["key"], "text of another project", forbid)
            if j["mode"] == "copy":
                assert pg["Title"] in text, (j["key"], "part mark not in PDF")
            for draw in page.get_drawings():
                rr = draw["rect"]
                if rr.x0 < -.5 or rr.y0 < -.5 or rr.x1 > page.rect.width + .5 or rr.y1 > page.rect.height + .5:
                    edge_flags.append((j["key"], i, list(rr)))
            merged.insert_pdf(doc)
            doc.close()
        if len(j["pages"]) > 1:
            merged.set_toc([[1, p["Number"] + " " + p["Title"], i + 1] for i, p in enumerate(j["pages"])])
        pdf = folder / (dwg.stem + ".pdf")
        assert not pdf.exists()
        merged.save(pdf, garbage=4, deflate=True)
        merged.close()
        resolved.append({"job": j, "qc": q, "dwg": target, "pdf": pdf})
    assert not edge_flags, ("vector graphics outside the paper", edge_flags)

    cons = [r for r in resolved if r["job"]["category"] != CATS["part"]]
    parts = [r for r in resolved if r["job"]["category"] == CATS["part"]]
    nidx = sum(r["job"]["category"] == CATS["index"] for r in cons)
    ncover = sum(r["job"]["category"] == CATS["cover"] for r in cons)
    np_ = sum(len(r["job"]["pages"]) for r in cons)
    nparts = sum(len(r["job"]["pages"]) for r in parts)
    assert np_ == len(R) + nidx + ncover, (np_, len(R), nidx, ncover)
    books = [(f"{name}_施工圖冊", cons, np_)] + ([(f"{name}_零件圖冊", parts, nparts)] if parts else [])
    for stem, records, pages in books:
        book, toc, number = f.open(), [], 1
        for r in records:
            doc = f.open(r["pdf"])
            book.insert_pdf(doc)
            for pg in r["job"]["pages"]:
                toc.append([1, (pg["Number"] + " " + pg["Title"]).strip(), number])
                number += 1
            doc.close()
        assert len(book) == pages
        book.set_toc(toc)
        p = D / (stem + ".pdf")
        book.save(p, garbage=4, deflate=True)
        book.close()
        with f.open(p) as check:
            idx = 0
            for r in records:
                with f.open(r["pdf"]) as one:
                    for page in one:
                        a = check[idx].get_pixmap(matrix=f.Matrix(.7, .7)).samples
                        assert a == page.get_pixmap(matrix=f.Matrix(.7, .7)).samples, (stem, idx)
                        idx += 1
            if stem.endswith("施工圖冊") and nidx:
                it = "".join(check[k].get_text() for k in range(ncover, ncover + nidx))
                assert CATS["part"] not in it, "parts listed in the drawing list"
                for row in R:
                    assert it.count(row["Number"]) == 1 and row["Title"] in it, row
                    assert row["Number"] in check[row["BookPage"] - 1].get_text(), row

    lookup = {pg["Number"]: r for r in cons for pg in r["job"]["pages"]}
    with (D / "施工圖號_來源對照表.csv").open("w", encoding="utf-8-sig", newline="") as s:
        wr = csv.writer(s)
        wr.writerow(["圖號", "分類", "圖名", "施工圖冊頁次", "原始圖檔", "原檔分頁", "比例", "交付DWG", "交付PDF"])
        for row in R:
            r = lookup[row["Number"]]
            scale = next(p["Scale"] for p in r["job"]["pages"] if p["Number"] == row["Number"])
            wr.writerow([row["Number"], row["Category"], row["Title"], row["BookPage"], row["Source"], row["FilePage"],
                         scale, r["dwg"].relative_to(D).as_posix(), r["pdf"].relative_to(D).as_posix()])

    cat = {c: sum(len(j["pages"]) for j in J if j["category"] == c) for c in (CATS["standard"], CATS["erection"], CATS["assembly"])}
    multis = "；".join(f"{Path(j['source']).name} 含 {len(j['pages'])} 張圖面：{', '.join(p['Number'] for p in j['pages'])}"
                      for j in J if len(j["pages"]) > 1) or "無"
    actions = {}
    for r in parts:
        a = (r["qc"].get("project_action") or "byte_identical").split(":")[0]
        actions.setdefault(a, []).append(Path(r["job"]["source"]).stem)
    parts_note = "；".join(f"{k} {len(v)}張" for k, v in sorted(actions.items())) or "無"
    lines = [
        f"{P.get('project_title', name)} — {P['batch']}",
        "",
        f"施工圖冊：{np_}頁（封面{ncover}、圖號清單{nidx}、標準圖{cat[CATS['standard']]}、安裝圖{cat[CATS['erection']]}、構件圖{cat[CATS['assembly']]}）。",
        f"零件圖冊：{nparts}頁，另冊，不列入圖號清單。零件圖處理：{parts_note}。",
        f"來源：{len(received)}張DWG（雜湊清單 05_交付紀錄/received-{P['batch']}-sha256.txt）。",
        f"多圖面來源：{multis}。",
        "舊修訂表清除：" + ("、".join(f"{r['source']}（{len(r['handles'])}個物件）" for r in REVR) or "無") + "。",
        "圖紙外來源標記（保留在DWG、不列印，請確認）：" + ("；".join(f"{o['source']} {o['type']} {o['text'] or ''} @ {[round(v) for v in o['extent']]}" for o in OFF) or "無") + "。",
        "未收錄：" + ("；".join(f"{k}：{v}" for k, v in excluded.items()) or "無") + "。",
        "工程視圖、尺寸、標註、BOM與原生標記保留；只修改圖框／資訊欄、圖號、圖名、比例欄與列印範圍。每張存檔後原生重開，逐 handle 比對其餘實體不變。",
        "PDF 為 A3 等比例適配完整圖框，施工依標示尺寸，不宣稱紙面可量測 1:1。",
        "本包為 detached DWG／PDF，不含 Advance Steel 模型或 Document Manager 登錄。",
        *P.get("notes_extra", []),
    ]
    (D / "交付說明.txt").write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    manifest = [{"source": Path(r["job"]["source"]).name, "source_sha256": r["job"]["source_sha256"], "category": r["job"]["category"],
                 "dwg": r["dwg"].relative_to(D).as_posix(), "dwg_sha256": sha(r["dwg"]),
                 "pdf": r["pdf"].relative_to(D).as_posix(), "pdf_sha256": sha(r["pdf"]), "pages": r["job"]["pages"],
                 "preserved_entities": r["qc"]["preserved_entities"], "parts_project_action": r["qc"].get("project_action"),
                 "byte_identical_to_source": r["qc"].get("byte_identical_to_source")} for r in resolved]
    jdump(D / "交付檢查與來源對照.json", {"project": P.get("project_title", name), "batch": P["batch"], "received": received,
                                    "excluded": excluded, "revision_tables_removed": REVR, "offsheet_source_warnings": OFF,
                                    "construction_pages": np_, "parts_pages": nparts, "index_rows": len(R), "manifest": manifest})
    files = sorted(p for p in D.rglob("*") if p.is_file())
    assert len(files) == len(J) * 2 + len(books) + 3, (len(files), len(J))
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, p.relative_to(D).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist()) == len(files)
        for rel in z.namelist():
            assert hashlib.sha256(z.read(rel)).hexdigest() == sha(D / rel), rel
    report = {"archive": str(archive), "archive_sha256": sha(archive), "bytes": archive.stat().st_size, "files": len(files),
              "construction_pages": np_, "parts_pages": nparts, "dwgs": len(J),
              "parts_actions": {k: len(v) for k, v in actions.items()}, "excluded": list(excluded)}
    jdump(P.records / "delivery_qc.json", report)
    print(report)


if __name__ == "__main__":
    main()
