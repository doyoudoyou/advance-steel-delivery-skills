"""Step 1 — read-only inventory of every source DWG (+ standards and cover) through Core Console.

Writes <work>/inventory/<stem>/inventory.json and, for frame-bearing sheets, the texts inside the
A$C frame (<work>/source_preview/<stem>/frame_texts.json) used to recover title / scale.
Re-runs skip sheets whose output already exists; delete a half-written folder before re-running.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .common import Project, jload


def main():
    P = Project.load()
    W = P.work
    items = [(p, W / "inventory" / p.stem) for p in P.sources()]
    std = P.get("standards")
    if std:
        items += [(p, W / "extra_inventory" / ("STD_" + p.stem)) for p in sorted(Path(std["dir"]).glob("*.dwg"))]
    if P.get("cover"):
        items.append((Path(P["cover"]["dwg"]), W / "extra_inventory" / "COVER"))
    frame_prefixes = tuple(c["prefix"] for c in P["categories"] if c["kind"] != "part")

    def work(item):
        p, w = item
        if (w / "inventory.json").exists():
            return p.name + " cached"
        es = P.entities(P.inspect(p, w))
        return f"{p.name} {len(es)} entities"

    def probe(p):
        w = W / "source_preview" / p.stem
        if (w / "frame_texts.json").exists():
            return p.name + " probe cached"
        P.run(p, w, "probe", ["DTPROBE"], {"DT_REPORT": w / "frame_texts.json"})
        texts = [x["TextString"] for x in jload(w / "frame_texts.json")]
        return f"{p.name} frame texts: {[t for t in texts if '比例' in t or '1:' in t][:4]}"

    probes = [p for p in P.sources() if p.name.startswith(frame_prefixes)]
    with ThreadPoolExecutor(max_workers=P.get("workers", 2)) as ex:
        fs = [ex.submit(work, x) for x in items] + [ex.submit(probe, p) for p in probes]
        for f in as_completed(fs):
            print(f.result(), flush=True)
    n = sum(1 for p in P.sources() if (W / "inventory" / p.stem / "inventory.json").exists())
    print(f"inventory {n}/{len(P.sources())} source DWGs")
    assert n == len(P.sources())


if __name__ == "__main__":
    main()
