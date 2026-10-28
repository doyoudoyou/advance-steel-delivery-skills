"""Step 2 — build jobs.json: drawing numbers, titles, scales, print windows, erase lists.

Stops (AssertionError) instead of guessing when:
  * a sheet's engineering entities do not fit any page window (see `exempt` / `offsheet` in the config)
  * an unexpected REVISIONS table is found
  * a frame-bearing sheet has no recoverable scale (erection / standard sheets fall back to config text)
  * an erection drawing id has no title in the config
  * the source count differs from `expected_source_count`
"""
import re
from pathlib import Path

from .common import CATS, Project, jdump, jload, sha


def main():
    P = Project.load()
    W = P.work
    win = {"left": -11, "right": 418, "bottom": -11, "top": 285, "info_band_bottom": 20.5, "max_shift": 40,
           **P.get("page_window", {})}
    exempt = {(e["source"], e["handle"]): e for e in P.get("exempt", [])}
    offsheet = {(o["source"], h): o for o in P.get("offsheet", []) for h in o["handles"]}
    rev = P.get("revision_cleanup")
    records, construction, off_found, rev_removed, shared_scale = [], [], [], [], []

    def inv_of(stem, extra=False):
        return jload(W / ("extra_inventory" if extra else "inventory") / stem / "inventory.json")

    def add(src, cat, numbers, title, inv, default_scale=None):
        es = P.entities(inv)
        erase = P.frame_handles(es)
        frames = [e for e in es if e["block"] and e["block"].startswith("A$C")] or \
                 [e for e in es if e["block"] == "HYPERSTEELPAGEFRAME"]
        assert frames, (src.name, "no A$C or HYPERSTEELPAGEFRAME frame found")
        left = sorted(e["extent"][0] for e in frames)
        xs = [round(v - left[0], 6) for v in left]
        assert len(xs) == len(numbers), (src.name, xs, numbers)

        # Old revision table: explicit rule only, never a blanket rectangle delete.
        if rev and cat in [CATS[c] for c in rev.get("categories", ["erection"])]:
            # leftover header words of the old table (e.g. Index/Date/Description/Author) are erased
            # on every sheet of these categories, matching exact text only
            erase += [e["handle"] for e in es if e["text"] in rev.get("extra_texts", [])]
            x0, y0, x1, y1 = rev["box"]
            box = [e for e in es if e["layer"] == rev.get("layer", "Page") and e["type"] in ("Line", "DBText")
                   and e["extent"] and x0 <= e["extent"][0] <= e["extent"][2] <= x1 and y0 <= e["extent"][1] <= e["extent"][3] <= y1]
            if box:
                assert any(e["text"] == rev.get("marker", "REVISIONS") for e in box), (src.name, "grid without marker", box)
                erase += [e["handle"] for e in box]
                rev_removed.append({"source": src.name, "handles": [e["handle"] for e in box]})
        left_rev = [e for e in es if e["text"] == "REVISIONS" and e["handle"] not in erase]
        assert not left_rev, ("Unexpected REVISIONS table; add an explicit revision_cleanup rule", src.name, left_rev)

        geom = [e for e in es if e["type"] != "Viewport" and e["handle"] not in erase and e["extent"]]
        probe = W / "source_preview" / src.stem / "frame_texts.json"
        prefix = P["donor"].get("scale_prefix", "比例：")
        scales = [t["TextString"].removeprefix(prefix) for t in jload(probe) if t["TextString"].startswith(prefix)] if probe.exists() else []
        if not scales:
            scales = [a["TextString"] for e in es if e["block"] == "HYPERSTEELPAGEHEADER"
                      for a in (e["attrs"] or []) if a["Tag"] == "SCALE" and a["TextString"].strip()]
        if len(scales) == 1 and len(xs) > 1:
            shared_scale.append({"source": src.name, "scale": scales[0], "pages": len(xs)})
            scales = scales * len(xs)
        if not scales:
            assert default_scale, ("Missing source frame scale; do not guess", src.name)
            scales = [default_scale] * len(xs)
        assert len(scales) == len(xs), (src.name, scales, xs)

        pages = []
        for i, x in enumerate(xs):
            scope = [e["extent"] for e in geom if e["extent"][0] >= x + win["left"] and e["extent"][2] <= x + win["right"]]
            assert scope, (src.name, x)
            shift = min(0, min(v[1] for v in scope) - win["info_band_bottom"])
            assert -win["max_shift"] <= shift <= 0, (src.name, "info band would move too far", shift)
            ttl = title + (f" ({i + 1}/{len(xs)})" if len(xs) > 1 else "")
            pg = {"Number": numbers[i], "Title": ttl, "X": x, "ShiftY": shift, "Scale": scales[i],
                  "Window": [x + win["left"], shift + win["bottom"], x + win["right"], win["top"]]}
            pages.append(pg)
            construction.append({"Number": pg["Number"], "Title": ttl, "Category": cat, "Source": src.name, "FilePage": i + 1})
        for e in geom:
            k = (src.name, e["handle"])
            if k in offsheet:
                off_found.append({"source": src.name, "handle": e["handle"], "type": e["type"], "text": e["text"],
                                  "extent": e["extent"], "reason": offsheet[k].get("reason", "")})
                continue
            if k in exempt:
                assert e["type"] == exempt[k].get("type", e["type"]), (k, e["type"])
                continue
            assert any(e["extent"][0] >= p["Window"][0] and e["extent"][2] <= p["Window"][2]
                       and e["extent"][1] >= p["Window"][1] and e["extent"][3] <= p["Window"][3] for p in pages), \
                (src.name, "engineering entity outside every page window — see skill rule 10/18", e)
        key = "_".join(numbers)
        w = W / "production" / key
        w.mkdir(parents=True, exist_ok=True)
        records.append({"key": key, "source": str(src), "source_sha256": sha(src), "category": cat, "mode": "apply",
                        "erase": erase, "pages": pages, "output": str(w / f"{key}_{src.name}"), "inventory": inv})

    # standards (ED) — optional, from an earlier verified set
    std = P.get("standards")
    if std:
        for i, p in enumerate(sorted(Path(std["dir"]).glob("*.dwg")), 1):
            add(p, CATS["standard"], [std.get("number", "ED-{:03d}").format(i)],
                std["titles"][i - 1].format(name=P.name), inv_of("STD_" + p.stem, True), std.get("default_scale", "NTS"))

    srcs = P.sources()
    claimed = set()
    for c in P["categories"]:
        kind = c["kind"]
        mine = [p for p in srcs if p.name.startswith(c["prefix"])]
        claimed |= set(mine)
        if kind == "part":
            continue
        seq = 0
        for p in mine:
            inv = inv_of(p.stem)
            es = P.entities(inv)
            count = sum(bool(e["block"] and e["block"].startswith("A$C")) for e in es) or \
                    sum(e["block"] == "HYPERSTEELPAGEFRAME" for e in es)
            m = re.search(c["id_regex"], p.name)
            assert m, (p.name, c["id_regex"])
            ident = m.group(1)
            if "titles" in c:
                assert ident in c["titles"], (p.name, f"no title for id {ident!r} in config — ask the user")
                title = c["title"].format(name=P.name, id=ident, title=c["titles"][ident])
            else:
                title = c["title"].format(name=P.name, id=ident)
            numbers = [c["number"].format(seq + i + 1) for i in range(count)]
            seq += count
            add(p, CATS[kind], numbers, title, inv, c.get("default_scale"))
    unclaimed = [p.name for p in srcs if p not in claimed]
    assert not unclaimed, ("source files matching no category", unclaimed)

    # cover + drawing-list pages
    ix = P.get("index", {})
    per = ix.get("rows_per_page", 20)
    nidx = (len(construction) + per - 1) // per
    for i, r in enumerate(construction, 2 + nidx):
        r["BookPage"] = i
    head = []
    if P.get("cover"):
        cv = P["cover"]
        cover = Path(cv["dwg"])
        inv = inv_of("COVER", True)
        w = W / "production" / "COVER"
        w.mkdir(parents=True, exist_ok=True)
        head.append({"key": "COVER", "source": str(cover), "source_sha256": sha(cover), "category": CATS["cover"],
                     "mode": "cover", "erase": [],
                     "pages": [{"Number": cv.get("number", "AF-001"), "Title": cv.get("title", "{name}").format(name=P.name),
                                "Window": [win["left"], win["bottom"], win["right"], win["top"]]}],
                     "output": str(w / "COVER.dwg"), "inventory": inv})
        for i in range(1, nidx + 1):
            key = ix.get("number", "AL-{:03d}").format(i)
            w = W / "production" / key
            w.mkdir(parents=True, exist_ok=True)
            head.append({"key": key, "source": str(cover), "source_sha256": sha(cover), "category": CATS["index"],
                         "mode": "index", "erase": [e["handle"] for e in P.entities(inv) if e["type"] != "Viewport"],
                         "pages": [{"Number": key, "Title": ix.get("title", "{name} - 圖號清單").format(name=P.name)
                                    + (f"({i}/{nidx})" if nidx > 1 else ""), "X": 0, "ShiftY": 0, "Scale": "NTS",
                                    "Window": [win["left"], win["bottom"], win["right"], win["top"]]}],
                         "output": str(w / f"{key}.dwg"), "rows": construction[(i - 1) * per:i * per], "inventory": inv})
    records = head + records

    part_cat = next((c for c in P["categories"] if c["kind"] == "part"), None)
    if part_cat:
        for p in [p for p in srcs if p.name.startswith(part_cat["prefix"])]:
            m = re.search(part_cat["id_regex"], p.name)
            assert m, (p.name, part_cat["id_regex"])
            w = W / "production" / p.stem
            w.mkdir(parents=True, exist_ok=True)
            records.append({"key": p.stem, "source": str(p), "source_sha256": sha(p), "category": CATS["part"],
                            "mode": "copy", "erase": [],
                            "pages": [{"Number": "", "Title": m.group(1), "Window": [win["left"], win["bottom"], win["right"], win["top"]]}],
                            "output": str(w / p.name), "inventory": inv_of(p.stem)})

    assert len(records) == len({r["key"] for r in records}), "duplicate job keys"
    exp = P.get("expected_source_count")
    assert exp is None or len(srcs) == exp, ("source count", len(srcs), exp)
    P.records.mkdir(parents=True, exist_ok=True)
    rec = P.records / f"received-{P['batch']}-sha256.txt"
    lines = "".join(f"{sha(p)} *{p.name}\n" for p in srcs)
    if rec.exists():
        assert rec.read_text(encoding="utf-8") == lines, ("received files changed since first prepare", str(rec))
    else:
        rec.write_text(lines, encoding="utf-8")
    for name, obj in [("jobs.json", records), ("construction_index.json", construction), ("shared_scale.json", shared_scale),
                      ("revision_removed.json", rev_removed), ("offsheet_warnings.json", off_found)]:
        jdump(W / name, obj)
    print("jobs", len(records), "| construction sheets", len(construction), "| index pages", nidx,
          "| parts", sum(r["mode"] == "copy" for r in records), "| revision tables removed", len(rev_removed),
          "| off-sheet warnings", len(off_found), "| shared scale", len(shared_scale))
    for r in records:
        if r["mode"] == "apply":
            print(" ", r["key"], [(p["Number"], p["Title"], round(p["ShiftY"], 2), p["Scale"]) for p in r["pages"]])


if __name__ == "__main__":
    main()
