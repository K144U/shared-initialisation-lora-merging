#!/usr/bin/env python3
"""Cells of notes/check_solve_precision_result_2026-10-24.md: the float64
rebuild of the one merge the B1 rule flagged (Yi seed1, encoder at lambda 0),
plus two unregistered controls.

  rd_l0_f64       registered: float64 solve, exact truncation
  rd_l0_rerun     control: the production configuration unchanged
  rd_l0_f32exact  control: float32 solve, exact truncation

  --seeds: the unregistered follow-up of the same note, float32 with
  production and with exact truncation at rng_seed 1 and 2.
  --sweep: the seed sweep on the other three bases (same note), float32
  with production truncation at rng_seed 1 and 2.
  --sweep23: the same sweep on shared cohorts seed2 and seed3 of all four
  bases, from the re-run cells in eval_ridge_shared
  (notes/rerun_lost_cells_2026-10-26.md, follow-up).

Template: the published cell eval_ridge_cond/<base>__rd_l0__seed1.json.
"""
from __future__ import annotations

import sys

from _c1019 import CACHE, INVARIANT, RES, Manifest, template

OUT_DIR = "eval_precision_f64"
BASE, COHORT = "yi15_9b", "seed1"
ARMS = {
    "rd_l0_f64": {"solve_dtype": "float64", "truncation": "exact"},
    "rd_l0_rerun": {},
    "rd_l0_f32exact": {"truncation": "exact"},
}


SEED_ARMS = {
    f"rd_l0_{t}_s{k}": {**extra, "rng_seed": k}
    for t, extra in (("rerun", {}), ("f32exact", {"truncation": "exact"}))
    for k in (1, 2)
}

SWEEP_BASES = ("llama31_8b", "mistral_7b", "qwen25_7b")
SWEEP_ARMS = {f"rd_l0_rerun_s{k}": {"rng_seed": k} for k in (1, 2)}
SWEEP23_BASES = ("llama31_8b", "mistral_7b", "qwen25_7b", "yi15_9b")
SWEEP23_COHORTS = ("seed2", "seed3")


def sweep23(m) -> None:
    for base in SWEEP23_BASES:
        for cohort in SWEEP23_COHORTS:
            t = template(RES / "eval_ridge_shared" / f"{base}__rds_l0__{cohort}.json")
            assert t["method"] == "rd_encoder" and float(t["method_kwargs"]["ridge_lambda"]) == 0.0
            for tag, extra in SWEEP_ARMS.items():
                name = f"{base}__{tag}__{cohort}"
                cfg = {k: v for k, v in t.items() if k != "output_path"}
                cfg.update(method_kwargs={**t["method_kwargs"], **extra},
                           nll_tau_cache=str(CACHE / f"{base}__{cohort}.json"),
                           output_path=str(RES / OUT_DIR / f"{name}.json"))
                for k in INVARIANT:
                    assert cfg.get(k) == t.get(k), (name, k)
                m.add(name, cfg, OUT_DIR, "run_eval_cell.py", min_free=40.0)
    m.write("precision_sweep23_manifest.json", expect=16)


def main() -> int:
    seeds = "--seeds" in sys.argv[1:]
    sweep = "--sweep" in sys.argv[1:]
    arms = SWEEP_ARMS if sweep else SEED_ARMS if seeds else ARMS
    m = Manifest()
    if "--sweep23" in sys.argv[1:]:
        sweep23(m)
        return 0
    for base in SWEEP_BASES if sweep else (BASE,):
        t = template(RES / "eval_ridge_cond" / f"{base}__rd_l0__{COHORT}.json")
        assert t["method"] == "rd_encoder" and float(t["method_kwargs"]["ridge_lambda"]) == 0.0
        for tag, extra in arms.items():
            name = f"{base}__{tag}__{COHORT}"
            cfg = {k: v for k, v in t.items() if k != "output_path"}
            cfg.update(method_kwargs={**t["method_kwargs"], **extra},
                       nll_tau_cache=str(CACHE / f"{base}__{COHORT}.json"),
                       output_path=str(RES / OUT_DIR / f"{name}.json"))
            for k in INVARIANT:
                assert cfg.get(k) == t.get(k), (name, k)
            m.add(name, cfg, OUT_DIR, "run_eval_cell.py", min_free=40.0)
    if sweep:
        m.write("precision_sweep_manifest.json", expect=6)
    elif seeds:
        m.write("precision_seeds_manifest.json", expect=4)
    else:
        m.write("precision_f64_manifest.json", expect=3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
