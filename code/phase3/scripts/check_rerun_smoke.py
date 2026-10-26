#!/usr/bin/env python3
"""Smoke inspection for the re-run of notes/rerun_lost_cells_2026-10-26.md.

Checks the two smoke cells of rerun_lost_smoke_manifest.json for what the
registrations' smoke constraint allows: the configuration the cell ran is the
one generated, nll_tau came from the cache, the merge is not a no-op, and the
scorer produced output for every item. It prints no excess and no accuracy, so
it reveals nothing about the direction of any effect.

  python code/phase3/scripts/check_rerun_smoke.py
"""
from __future__ import annotations

import json
import sys

import yaml

from _c1019 import CFG, ROOT


def main() -> int:
    bad = []
    for cell in json.loads((CFG / "rerun_lost_smoke_manifest.json").read_text()):
        p = ROOT / cell["done"]
        if not p.exists():
            print(f"{cell['name']}: not landed yet")
            return 1
        r = json.loads(p.read_text())
        ran = json.loads(json.dumps(r["meta"]["config"]))
        gen = yaml.safe_load((ROOT / cell["cmd"].split("--config ")[1]).read_text())
        # The harness records its merge-cache key in method_kwargs; not a setting.
        ran.get("method_kwargs", {}).pop("_merge_cache_key", None)
        diff = sorted(k for k in set(ran) | set(gen) if ran.get(k) != gen.get(k))
        ok_cfg = not diff
        print(f"{cell['name']}: config equals the generated one: {ok_cfg} {diff or ''}")
        bad += [] if ok_cfg else [cell["name"] + " config"]
        if "nll_tau" in r:
            hit = r.get("nll_tau_from_cache") is True
            moved = any(abs(r["nll_merged"][t] - r["nll_tau"]["base"][t]) > 1e-6
                        for t in r["nll_merged"])
            # rd_encoder is not in the harness's DIAG_MODULES, so merge_diagnostics
            # is None on every encoder cell; its own summary line is in the log.
            log = ROOT / "logs" / "orch" / f"{cell['name']}.log"
            enc = [ln.strip() for ln in log.read_text().splitlines()
                   if ln.startswith("[rd_encoder]")] if log.exists() else []
            print(f"    nll_tau from cache: {hit}; merged differs from base: {moved}")
            print(f"    {enc[-1] if enc else 'no [rd_encoder] line in ' + str(log)}")
            bad += [] if hit and moved and enc else [cell["name"] + " nll"]
        else:
            pe = r["per_example"]
            empty = sum(not (e.get("gen_raw") or e.get("gen_text")) for e in pe)
            print(f"    items {len(pe)} of n_eval_metric {r['n_eval_metric']} "
                  f"(registered {gen['n_eval_metric']}); empty generations {empty}")
            bad += [] if len(pe) == gen["n_eval_metric"] and empty == 0 else [cell["name"] + " yield"]
    print("SMOKE OK" if not bad else f"SMOKE FAILED: {bad}")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
