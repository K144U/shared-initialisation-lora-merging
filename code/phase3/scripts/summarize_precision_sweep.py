#!/usr/bin/env python3
"""Seed sweep of notes/check_solve_precision_result_2026-10-24.md: per base,
the float32 encoder at lambda 0 on the shared cohort under the default stream
(the published cell) and rng_seed 1 and 2, against the independent cell.

--sweep23: the same on seed2 and seed3, read as fixed in the follow-up of
notes/rerun_lost_cells_2026-10-26.md: per cohort the three draws (re-run
default, s1, s2) and their range against the independent mean; per base the
nine seed2 + seed3 sums against the sum the lost run implies; and whether every
combination keeps the shared-over-independent ratio at or above 2.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results" / "phase3"
BASES = ("llama31_8b", "mistral_7b", "qwen25_7b", "yi15_9b")


def load(p):
    return json.loads(p.read_text())


# Lost seed2 + seed3 sums at lambda = 0, implied by the published ratios
# (4.42, 76.2, 10.8, 2.82 x the independent mean) and the reused seed1 cell.
LOST_SUM = {"llama31_8b": 0.636, "mistral_7b": 25.38, "qwen25_7b": 0.648, "yi15_9b": 0.789}


def sweep23() -> int:
    for b in BASES:
        s1 = load(RES / "eval_ridge_cond" / f"{b}__rd_l0__seed1.json")["worst_task_excess"]
        ind = [load(RES / "eval_ridge_cond" / f"{b}__rd_l0__indep1.json")["worst_task_excess"]]
        ind += [load(RES / "eval_ridge_cohorts" / f"{b}__rdc_l0__{c}.json")["worst_task_excess"]
                for c in ("indep2", "indep3")]
        im = sum(ind) / 3
        w = {}
        for c in ("seed2", "seed3"):
            reg = load(RES / "eval_ridge_shared" / f"{b}__rds_l0__{c}.json")
            draws = {"default": reg}
            for k in (1, 2):
                draws[f"s{k}"] = load(RES / "eval_precision_f64" / f"{b}__rd_l0_rerun_s{k}__{c}.json")
            for tag, d in draws.items():
                assert d["nll_tau"] == reg["nll_tau"], (b, c, tag)
                assert d["method_kwargs"].get("rng_seed") == (None if tag == "default" else int(tag[1:])), (b, c, tag)
            w[c] = {t: d["worst_task_excess"] for t, d in draws.items()}
            v = list(w[c].values())
            print(f"{b:<11} {c} " + "  ".join(f"{t} {x:.4f}" for t, x in w[c].items())
                  + f"  range {max(v) - min(v):.4f}  indep mean {im:.4f}  all_above {all(x > im for x in v)}")
        sums = [x + y for x in w["seed2"].values() for y in w["seed3"].values()]
        ratios = [(s1 + x) / 3 / im for x in sums]
        lost = LOST_SUM[b]
        print(f"{'':<11} sums {min(sums):.4f} to {max(sums):.4f}  lost {lost:.4f}  "
              f"lost_inside {min(sums) <= lost <= max(sums)}  "
              f"ratio {min(ratios):.2f} to {max(ratios):.2f}  all_ratio_ge_2 {all(r >= 2 for r in ratios)}")
    return 0


def main() -> int:
    if "--sweep23" in sys.argv[1:]:
        return sweep23()
    for b in BASES:
        pub = load(RES / "eval_ridge_cond" / f"{b}__rd_l0__seed1.json")
        ind = load(RES / "eval_ridge_cond" / f"{b}__rd_l0__indep1.json")
        draws = {"default": pub}
        for k in (1, 2):
            draws[f"s{k}"] = load(RES / "eval_precision_f64" / f"{b}__rd_l0_rerun_s{k}__seed1.json")
        for tag, d in draws.items():
            assert d["nll_tau"] == pub["nll_tau"], (b, tag)
            assert d["method_kwargs"].get("rng_seed") == (None if tag == "default" else int(tag[1:])), (b, tag)
        w = {t: d["worst_task_excess"] for t, d in draws.items()}
        a = {t: d["avg_task_excess"] for t, d in draws.items()}
        iw = ind["worst_task_excess"]
        lo, hi = min(w.values()), max(w.values())
        print(f"{b:<11} worst " + "  ".join(f"{t} {v:.4f}" for t, v in w.items())
              + f"  range {hi - lo:.4f}  indep {iw:.4f}  gap(min-indep) {lo - iw:.4f}"
              + f"  all_above {all(v > iw for v in w.values())}")
        print(f"{'':<11} avg   " + "  ".join(f"{t} {v:.4f}" for t, v in a.items()))
        for t, d in draws.items():
            print(f"{'':<11}   {t:<8}" + "  ".join(f"{k} {v:.4f}" for k, v in d["excess_per_task"].items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
