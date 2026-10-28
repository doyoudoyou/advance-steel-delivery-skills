"""Shared runtime: project config, Core Console runner, hashing, inventory helpers.

Every script takes the project config path as its first argument:
    python -m asdeliver.inventory  path/to/project.json
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

FRAME_BLOCKS = ("HYPERSTEELPAGEFRAME", "HYPERSTEELPAGEHEADER", "ADVANCESTEEL_RESERVED_AREA")
CATS = {"standard": "標準圖", "erection": "安裝圖", "assembly": "構件圖", "part": "零件圖",
        "cover": "封面", "index": "圖號清單"}


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def natural(p: Path):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", p.name)]


def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def jdump(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class Project:
    cfg: dict
    path: Path

    @classmethod
    def load(cls, argv=None) -> "Project":
        argv = sys.argv[1:] if argv is None else argv
        if not argv:
            sys.exit("usage: python -m asdeliver.<step> project.json [keys...]")
        p = Path(argv[0]).resolve()
        return cls(jload(p), p)

    def __getitem__(self, k):
        return self.cfg[k]

    def get(self, k, d=None):
        return self.cfg.get(k, d)

    @property
    def name(self) -> str:
        return self.cfg["name"]

    @property
    def root(self) -> Path:
        return Path(self.cfg["root"])

    @property
    def work(self) -> Path:            # 02_工作暫存/<batch>
        return self.root / "02_工作暫存" / self.cfg["batch"]

    @property
    def pending(self) -> Path:         # 03_待確認交付
        return self.root / "03_待確認交付"

    @property
    def records(self) -> Path:         # 05_交付紀錄
        return self.root / "05_交付紀錄"

    @property
    def source_dir(self) -> Path:
        return Path(self.cfg["source_dir"])

    @property
    def layout(self) -> str:
        return self.cfg.get("layout", "A3 Advance Steel")

    @property
    def number_layer(self) -> str:
        return self.cfg["donor"].get("number_layer", "DT_DRAWING_NUMBER")

    def sources(self):
        return sorted(self.source_dir.glob("*.dwg"), key=natural)

    # ---- Core Console ---------------------------------------------------------------------
    def run(self, src, work, tag, commands, env):
        """Copy src to a throw-away input, run commands in accoreconsole, prove src unchanged."""
        work = Path(work)
        work.mkdir(parents=True, exist_ok=True)
        before = sha(src)
        inp = work / f"{tag}-input.dwg"
        inp.write_bytes(Path(src).read_bytes())
        dll = Path(self.cfg["dll"]).as_posix()
        if not dll.isascii():
            raise SystemExit("dll path must be ASCII (NETLOAD mis-decodes non-ASCII paths)")
        scr = work / f"{tag}.scr"
        scr.write_text("_.FILEDIA\n0\n_.NETLOAD\n\"" + dll + "\"\n" + "\n".join(commands) + "\n_.QUIT\n_N\n",
                       encoding="ascii")
        e = os.environ.copy()
        e["DT_LAYOUT"] = self.layout
        e.update({k: str(v) for k, v in env.items()})
        cp = subprocess.run([self.cfg["accoreconsole"], "/i", str(inp.resolve()), "/s", str(scr.resolve()),
                             "/l", self.cfg.get("cad_language", "en-US")],
                            env=e, capture_output=True, timeout=self.cfg.get("cad_timeout_s", 300),
                            cwd=work)   # accoreconsole drops ErrorReports/ and plot.log into the cwd
        (work / f"{tag}.log").write_bytes(cp.stdout + cp.stderr)
        assert cp.returncode == 0, (src, cp.returncode)
        assert sha(src) == before, ("SOURCE_CHANGED", str(src))

    def inspect(self, src, w):
        w = Path(w)
        r = w / "inventory.json"
        self.run(src, w, "inspect", ["DTINSPECT"], {"DT_REPORT": r})
        assert r.exists(), ("no inventory written (check NETLOAD / trusted paths)", str(src), str(w / "inspect.log"))
        return jload(r)

    def entities(self, inv):
        return next(x["entities"] for x in inv["layouts"] if x["name"] == self.layout)

    def frame_handles(self, es):
        """Old frame/header/reserved-area blocks and previous drawing-number markers to erase."""
        layers = {self.number_layer, *self.cfg.get("extra_erase_layers", [])}
        return [x["handle"] for x in es
                if (x["block"] and (x["block"].startswith("A$C") or x["block"] in FRAME_BLOCKS))
                or x["layer"] in layers]


def check_report(p):
    r = jload(p)
    assert r.get("success"), r
    return r
