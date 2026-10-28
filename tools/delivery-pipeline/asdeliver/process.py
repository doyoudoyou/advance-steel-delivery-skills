"""Step 3 — per job: apply frame / cover / index / part PROJECT fill, save, native reopen, plot PDFs,
then prove every non-target entity is unchanged (handle, type, layer, text, block, attrs, geometry).

    python -m asdeliver.process project.json              # all jobs
    python -m asdeliver.process project.json GA-001 COVER # selected keys (trial run first!)

A job with qc.json is skipped after re-verifying its DWG hash.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import Project, check_report, jdump, jload, sha


def main():
    P = Project.load()
    W = P.work
    jobs = jload(W / "jobs.json")
    donor_cfg = P["donor"]
    cover_cfg = P.get("cover", {})
    parts_cfg = P.get("parts", {})
    name = P.name
    cover_from = cover_cfg.get("replace_from")

    def compare(j, d):
        old = {x["name"]: x for x in j["inventory"]["layouts"]}
        new = {x["name"]: x for x in d["layouts"]}
        assert old.keys() == new.keys(), j["key"]
        n = 0
        for lname, lay in old.items():
            target = {e["handle"]: e for e in new[lname]["entities"]}
            for e in lay["entities"]:
                if e["handle"] in j["erase"]:
                    assert e["handle"] not in target, (j["key"], e["handle"], "should be erased")
                    continue
                if e["type"] == "Viewport" and e["vp"]["Number"] == 1:   # layout auto-viewport is recomputed
                    continue
                assert e["handle"] in target, (j["key"], e["handle"], "missing after reopen")
                t = target[e["handle"]]
                cover_text = j["mode"] == "cover" and cover_from and e["text"] and cover_from in e["text"]
                header = j["mode"] == "copy" and e["block"] == parts_cfg.get("block", "HYPERSTEELPAGEHEADER")
                for k in ("type", "layer", "text", "block", "attrs", "vp"):
                    if k == "text" and cover_text:
                        assert t[k] == e[k].replace(cover_from, name), (j["key"], e["handle"])
                        continue
                    if k == "attrs" and header:
                        for a, b in zip(e["attrs"], t["attrs"]):
                            if a["Tag"] == parts_cfg.get("tag", "PROJECT"):
                                assert b["TextString"] == (name if a["TextString"] in ("", name) else a["TextString"]), (j["key"], a, b)
                            else:
                                assert a == b, (j["key"], a, b)
                        continue
                    assert e[k] == t[k], (j["key"], e["handle"], k, e[k], t[k])
                if cover_text or header:      # their extents legitimately change
                    n += 1
                    continue
                if e["extent"] is not None:
                    assert t["extent"] is not None and all(abs(a - b) < 1e-6 for a, b in zip(e["extent"], t["extent"])), \
                        (j["key"], e["handle"], "geometry", e["extent"], t["extent"])
                n += 1
        if j["mode"] in ("apply", "index"):
            markers = [e["text"] for e in P.entities(d) if e["layer"] == P.number_layer]
            assert sorted(markers) == sorted(p["Number"] for p in j["pages"]), (j["key"], markers)
        return n

    def process(j):
        w = W / "production" / j["key"]
        final = w / "qc.json"
        out = Path(j["output"])
        src = Path(j["source"])
        assert sha(src) == j["source_sha256"], ("source changed since prepare", j["key"])
        if final.exists():
            q = jload(final)
            assert q["dwg_sha256"] == sha(out)
            return j["key"] + " verified previously"
        project_action = None
        if j["mode"] == "copy":
            if parts_cfg.get("fill_project"):
                if not out.exists() or not (w / "project.json").exists():
                    out.unlink(missing_ok=True)
                    P.run(src, w, "project", ["DTPROJFILL"],
                          {"DT_OUTPUT": out, "DT_REPORT": w / "project.json", "DT_NAME": name,
                           "DT_BLOCK": parts_cfg.get("block", "HYPERSTEELPAGEHEADER"), "DT_TAG": parts_cfg.get("tag", "PROJECT"),
                           "DT_HEIGHT": parts_cfg.get("height", 2.5), "DT_ALIGNY": parts_cfg.get("align_y", 18.5)})
                project_action = check_report(w / "project.json")["action"]
            elif not out.exists():
                out.write_bytes(src.read_bytes())       # byte-identical copy
        elif not out.exists():
            env, cmd, reports = {}, [], []
            if j["mode"] in ("apply", "index"):   # index pages = cover DWG emptied + project frame + table
                ap = {"Donor": donor_cfg["dwg"], "Output": str(out), "Report": str(w / "apply.json"), "Erase": j["erase"],
                      "Pages": [{k: p[k] for k in ("Number", "Title", "X", "ShiftY", "Scale")} for p in j["pages"]],
                      "DonorTitleText": donor_cfg["title_text"], "DonorScaleText": donor_cfg.get("scale_text", "比例：NTS"),
                      "ScalePrefix": donor_cfg.get("scale_prefix", "比例："), "ScaleFallback": donor_cfg.get("scale_fallback", "詳各視圖"),
                      "NumberPos": donor_cfg["number_pos"], "MarkPos": donor_cfg.get("mark_pos"),
                      "NumberLayer": P.number_layer, "BottomBandY": donor_cfg.get("bottom_band_y", 26.0),
                      "MinDonorEntities": donor_cfg.get("min_entities", 50)}
                jdump(w / "apply-job.json", ap)
                env["DT_JOB"] = w / "apply-job.json"
                cmd = ["DTAPPLY"]
                reports = ["apply.json"]
            if j["mode"] == "cover":
                cmd = ["DTCOVER"]
                env.update(DT_OUTPUT=out, DT_REPORT=w / "cover.json", DT_FROM=cover_from, DT_TO=name,
                           DT_EXPECT_COUNT=cover_cfg.get("expect_count", 0))
                reports = ["cover.json"]
            if j["mode"] == "index":
                ix = P.get("index", {})
                jdump(w / "rows.json", j["rows"])
                jdump(w / "index-job.json", {"Output": str(out), "Report": str(w / "index.json"), "RowsFile": str(w / "rows.json"),
                                             "Title": ix.get("table_title", "{name} — 圖號清單").format(name=name),
                                             "Subtitle": ix.get("subtitle", "標準圖／安裝圖／構件圖"),
                                             "MaxRows": ix.get("rows_per_page", 20), "FontFile": ix.get("font", "kaiu.ttf")})
                env["DT_INDEX_JOB"] = w / "index-job.json"
                cmd.append("DTINDEX")
                reports.append("index.json")
            try:
                P.run(src, w, "apply", cmd, env)
                for r in reports:
                    check_report(w / r)
            except Exception:
                # never leave a half-made output behind: a rerun would otherwise treat it as done
                for leftover in (out, out.with_suffix(".upd")):
                    leftover.unlink(missing_ok=True)
                raise
        assert out.exists(), (j["key"], "no output")
        plots = [{"Pdf": str(w / f"page_{i + 1}.pdf"), "Report": str(w / f"plot_{i + 1}.json"), "Window": p["Window"]}
                 for i, p in enumerate(j["pages"])]
        for p in plots:
            for k in ("Pdf", "Report"):
                Path(p[k]).unlink(missing_ok=True)
        P.run(out, w, "reopen-plot", ["DTINSPECT", "DTPLOTALL"],
              {"DT_REPORT": w / "reopened.json", "DT_PLOTS": json.dumps(plots, ensure_ascii=False)})
        d = jload(w / "reopened.json")
        n = compare(j, d)
        for p in plots:
            check_report(p["Report"])
            assert Path(p["Pdf"]).stat().st_size > 1000
        q = {"key": j["key"], "success": True, "source_sha256": sha(src), "dwg_sha256": sha(out), "preserved_entities": n,
             "native_reopened": True, "pdfs": [p["Pdf"] for p in plots], "pdf_sha256": [sha(p["Pdf"]) for p in plots],
             "project_action": project_action, "byte_identical_to_source": sha(out) == sha(src)}
        jdump(final, q)
        return f"{j['key']} OK preserved={n}" + (f" project={project_action}" if project_action else "")

    sel = set(sys.argv[2:])
    todo = [j for j in jobs if not sel or j["key"] in sel]
    assert todo, ("no job matches", sel)
    failed = 0
    with ThreadPoolExecutor(max_workers=P.get("workers", 2)) as ex:
        fut = {ex.submit(process, j): j for j in todo}
        for f in as_completed(fut):
            try:
                print(f.result(), flush=True)
            except Exception as err:   # report every failure, keep the others running
                failed += 1
                print("FAILED", fut[f]["key"], repr(err)[:800], flush=True)
    print(f"done {len(todo) - failed}/{len(todo)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
