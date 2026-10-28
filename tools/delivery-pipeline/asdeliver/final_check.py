"""Step 6 — fresh-extract the ZIP and natively reopen the delivered DWGs.

Every changed sheet (frame/cover/index) plus `final_check_part_samples` parts (default: 4 evenly
spaced) are reopened in Core Console from the *extracted* copy and compared entity-by-entity with
the production read-back. Also re-hashes all received source files.
Re-run: delete <work>/fresh_extract and <work>/fresh_native_check first.
"""
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import Project, jdump, jload, sha


def main():
    P = Project.load()
    W = P.work
    name = P.name
    Q = jload(P.records / "delivery_qc.json")
    excluded = P.get("excluded", {})
    J = [j for j in jload(W / "jobs.json") if j["key"] not in excluded]
    ex = W / "fresh_extract"
    assert not ex.exists(), ("delete before re-running", str(ex))
    ex.mkdir()
    assert sha(Q["archive"]) == Q["archive_sha256"]
    with zipfile.ZipFile(Q["archive"]) as z:
        assert z.testzip() is None and len(z.namelist()) == Q["files"]
        for rel in z.namelist():
            p = ex / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(z.read(rel))
    M = jload(ex / "交付檢查與來源對照.json")
    for m in M["manifest"]:
        assert sha(ex / m["dwg"]) == m["dwg_sha256"] and sha(ex / m["pdf"]) == m["pdf_sha256"], m["dwg"]
    parts = [j["key"] for j in J if j["mode"] == "copy"]
    samples = P.get("final_check_part_samples")
    if samples is None:
        samples = [parts[i * (len(parts) - 1) // 3] for i in range(4)] if len(parts) >= 4 else parts
    selected = [j["key"] for j in J if j["mode"] != "copy"] + list(dict.fromkeys(samples))
    forbid = [n for n in P.get("forbidden_texts", []) if n != name]

    def verify(key):
        j = next(j for j in J if j["key"] == key)
        m = next(m for m in M["manifest"] if Path(m["dwg"]).name == Path(j["output"]).name)
        w = W / "fresh_native_check" / key
        src = ex / m["dwg"]
        P.run(src, w, "inspect", ["DTINSPECT"], {"DT_REPORT": w / "inventory.json"})
        actual = jload(w / "inventory.json")
        expected = jload(W / "production" / key / "reopened.json")
        for lay in expected["layouts"]:
            ee = {e["handle"]: e for e in lay["entities"] if e["type"] != "Viewport"}
            aa = {e["handle"]: e for e in next(n for n in actual["layouts"] if n["name"] == lay["name"])["entities"] if e["type"] != "Viewport"}
            assert aa == ee, (key, lay["name"], "differs from production read-back")
        if j["mode"] in ("apply", "index"):
            P.run(src, w, "frame", ["DTCHECKFRAME"], {"DT_REPORT": w / "frame.json"})
            frames = jload(w / "frame.json")
            assert len(frames) == len(j["pages"]), (key, len(frames))
            texts = [t["text"] for r in frames for t in r["texts"]]
            prefix = P["donor"].get("scale_prefix", "比例：")
            for p in j["pages"]:
                assert p["Title"] in texts and prefix + p["Scale"] in texts, (key, p["Title"], p["Scale"])
            assert not any("REVISIONS" in s.upper() or any(n in s for n in forbid) for s in texts), key
        return {"key": key, "dwg_sha256": sha(src), "entities_match": True, "native_reopened": True}

    results = []
    with ThreadPoolExecutor(max_workers=P.get("workers", 2)) as pool:
        for fu in as_completed([pool.submit(verify, k) for k in selected]):
            r = fu.result()
            results.append(r)
            print(r["key"], "fresh native match", flush=True)
    for line in (P.records / f"received-{P['batch']}-sha256.txt").read_text(encoding="utf-8").splitlines():
        h, n = line.split(None, 1)
        assert sha(P.source_dir / n.lstrip("*")) == h, ("received file changed", n)
    jdump(P.records / "fresh_native_qc.json", {"success": True, "zip_members": Q["files"], "native_reopened": len(results),
                                               "results": sorted(results, key=lambda r: r["key"]), "all_sources_unchanged": True})
    print("FINAL PASS", len(results))


if __name__ == "__main__":
    main()
