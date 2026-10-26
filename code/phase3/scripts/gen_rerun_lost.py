#!/usr/bin/env python3
"""Re-run of two tests whose per-cell files were lost on 2026-10-10.

Rules: notes/rerun_lost_cells_2026-10-26.md (b9d0e41), which leaves the
original registrations in force unchanged:

  shared arm at n = 3    notes/prereg_shared_arm_2026-08-15.md (603e013)
                         56 NLL cells, eval_ridge_shared, as gen_shared_arm.py
  downstream condition.  notes/prereg_downstream_2026-08-15.md (df832fe),
                         amendment 4d48987; 32 accuracy cells,
                         eval_downstream_cond, as gen_downstream_conditioning.py

The original per-cell YAML files went with the tree, so the template both
original generators used, eval_a1_indep/<base>__rd_ridge__indep1, is read from
the configuration embedded in that published result file and re-pointed at the
re-staged models and adapters. Everything else follows the two originals,
including their invariance checks, and no manifest is written if any fails:

  shared arm  1. seed2 and seed3 differ only in the adapter directory;
              2. every cell equals the published seed1 cell at the same lambda
                 (eval_ridge_cond) on base_model, max_seq_length, seed,
                 min_free_gb, loader, method, method_kwargs and task configs;
              3. the same against the published indep2 cell (eval_ridge_cohorts),
                 which the registration says was checked before it was written.
  downstream  1. seed1 and indep1 differ only in the adapter directory;
              2. every cell matches the NLL cell it is compared against;
              3. n_eval_metric is the amended value for its benchmark.

lambda* is read from the published eval_ridge_cond cells, never fitted here.
nll_tau comes from nll_tau_cache_v2, whose seed2/seed3 entries carry the same
key as the seed1 ones; run_eval_cell refuses a mismatched entry.

Usage (on the cluster, RDMERGE_ROOT set by pbs_v2.sh or by hand):
  python code/phase3/scripts/gen_rerun_lost.py
"""
from __future__ import annotations

import json
import sys

from _c1019 import BASES, CACHE, CFG, RES, Manifest, retarget, template

TAGS = ["0", "0p01", "0p03", "0p05", "0p13", "0p30", "1p00"]
LAM = {"0": 0.0, "0p01": 0.01, "0p03": 0.03, "0p05": 0.05,
       "0p13": 0.13, "0p30": 0.30, "1p00": 1.00}
REALIZE = "rank_r"
ARM_INVARIANT = ["base_model", "max_seq_length", "seed", "min_free_gb", "loader"]

SH_DIR, SH_COHORTS = "eval_ridge_shared", ["seed2", "seed3"]
DS_DIR, DS_COHORTS = "eval_downstream_cond", ["seed1", "indep1"]

# Amended per 4d48987: HumanEval's whole test split is 164 problems.
BENCH = {
    "gsm8k": {
        "metric": "gsm8k_em", "metric_task_spec": "gsm8k",
        "n_eval_metric": 500, "max_new_tokens": 256,
    },
    "humaneval": {
        "metric": "humaneval_pass1", "metric_task_spec": "humaneval",
        "n_eval_metric": 164, "max_new_tokens": 512,
        "metric_task_cfg": {
            "name": "humaneval", "dataset": "openai/openai_humaneval",
            "config": None, "split_train": "test", "split_eval": "test",
            "n_train": 0, "n_eval": 164,
            "prompt_field": "prompt", "answer_field": "canonical_solution",
        },
    },
}


def tasks(cfg):
    return [s.get("task_cfg") for s in cfg["adapter_specs"]]


def encoder_cfg(tmpl, specs, lam):
    cfg = {k: v for k, v in tmpl.items() if k != "output_path"}
    kw = dict(tmpl.get("method_kwargs", {}))
    kw.update(ridge_lambda=lam, realize=REALIZE)
    cfg.update(method="rd_encoder", method_kwargs=kw, adapter_specs=specs)
    return cfg


def same(a, b, keys, what, problems):
    for k in keys:
        if a.get(k) != b.get(k):
            problems.append(f"{what}: differs in {k} ({a.get(k)!r} vs {b.get(k)!r})")


def read_lstar(base, cohort):
    """lambda* = arg-min over the published E2 grid. Read, never fitted."""
    v = {t: json.loads((RES / "eval_ridge_cond" / f"{base}__rd_l{t}__{cohort}.json")
                       .read_text())["worst_task_excess"] for t in TAGS}
    return min(v, key=v.get)


def shared_arm(m, problems):
    for base in BASES:
        tmpl = template(RES / "eval_a1_indep" / f"{base}__rd_ridge__indep1.json")
        written = {}
        for cohort in SH_COHORTS:
            specs = retarget(tmpl["adapter_specs"], "indep1", cohort)
            for tag in TAGS:
                name = f"{base}__rds_l{tag}__{cohort}"
                cfg = encoder_cfg(tmpl, specs, LAM[tag])
                cfg.update(nll_tau_cache=str(CACHE / f"{base}__{cohort}.json"),
                           output_path=str(RES / SH_DIR / f"{name}.json"))
                written[cohort, tag] = cfg
                m.add(name, cfg, SH_DIR, "run_eval_cell.py")

        for tag in TAGS:
            a, b = written["seed2", tag], written["seed3", tag]
            same(a, b, ARM_INVARIANT + ["method", "method_kwargs"],
                 f"{base} {tag} seed2 vs seed3", problems)
            if tasks(a) != tasks(b):
                problems.append(f"{base} {tag}: task_cfg differs between cohorts")
            if {s["dir"] for s in a["adapter_specs"]} & {s["dir"] for s in b["adapter_specs"]}:
                problems.append(f"{base} {tag}: cohorts share an adapter directory")
            for ref_p in (RES / "eval_ridge_cond" / f"{base}__rd_l{tag}__seed1.json",
                          RES / "eval_ridge_cohorts" / f"{base}__rdc_l{tag}__indep2.json"):
                ref = template(ref_p)
                same(ref, a, ARM_INVARIANT + ["method", "method_kwargs"],
                     f"{base} {tag} vs published {ref_p.name}", problems)
                if tasks(ref) != tasks(a):
                    problems.append(f"{base} {tag}: task_cfg differs from {ref_p.name}")


def downstream(m, problems):
    lstars = {}
    for base in BASES:
        tmpl = template(RES / "eval_a1_indep" / f"{base}__rd_ridge__indep1.json")
        written = {}
        for cohort in DS_COHORTS:
            star = read_lstar(base, cohort)
            lstars[f"{base}|{cohort}"] = star
            specs = retarget(tmpl["adapter_specs"], "indep1", cohort)
            for which, tag in (("l0", "0"), ("lstar", star)):
                for bench, bspec in BENCH.items():
                    name = f"{base}__{which}_{bench}__{cohort}"
                    cfg = encoder_cfg(tmpl, specs, LAM[tag])
                    cfg.update(metric=bspec["metric"],
                               metric_task_spec=bspec["metric_task_spec"],
                               metric_kwargs={"max_new_tokens": bspec["max_new_tokens"]},
                               n_eval_metric=bspec["n_eval_metric"])
                    if "metric_task_cfg" in bspec:
                        cfg["metric_task_cfg"] = bspec["metric_task_cfg"]
                    cfg["output_path"] = str(RES / DS_DIR / f"{name}.json")
                    written[cohort, which, bench] = cfg
                    m.add(name, cfg, DS_DIR, "run_downstream_cell.py")

        for which in ("l0", "lstar"):
            for bench in BENCH:
                a, b = written["seed1", which, bench], written["indep1", which, bench]
                same(a, b, ARM_INVARIANT + ["metric", "n_eval_metric"],
                     f"{base} {which} {bench} seed1 vs indep1", problems)
                if {s["dir"] for s in a["adapter_specs"]} & {s["dir"] for s in b["adapter_specs"]}:
                    problems.append(f"{base} {which} {bench}: cohorts share a directory")
        for cohort in DS_COHORTS:
            ref = template(RES / "eval_ridge_cond" / f"{base}__rd_l0__{cohort}.json")
            if ref["method_kwargs"].get("realize") != REALIZE:
                problems.append(f"{base} {cohort}: NLL reference is not {REALIZE}")
            for which, tag in (("l0", "0"), ("lstar", lstars[f"{base}|{cohort}"])):
                ref = template(RES / "eval_ridge_cond" / f"{base}__rd_l{tag}__{cohort}.json")
                for bench in BENCH:
                    new = written[cohort, which, bench]
                    same(ref, new, ARM_INVARIANT + ["method", "method_kwargs"],
                         f"{base} {cohort} {which} {bench} vs its NLL cell", problems)
                    if tasks(ref) != tasks(new):
                        problems.append(f"{base} {cohort} {bench}: task_cfg differs from NLL cell")
        for (cohort, which, bench), c in written.items():
            if c["n_eval_metric"] != BENCH[bench]["n_eval_metric"]:
                problems.append(f"{base} {cohort} {which} {bench}: wrong n_eval_metric")
    return lstars


def main() -> int:
    problems: list[str] = []
    sh, ds = Manifest(), Manifest()
    shared_arm(sh, problems)
    lstars = downstream(ds, problems)
    if problems:
        print("PROBLEMS, no manifest written:")
        for p in sorted(set(problems)):
            print("  ", p)
        return 2

    (CFG / "downstream_cond_lstar.json").write_text(json.dumps(lstars, indent=2))
    print("lambda* read from eval_ridge_cond:", lstars)
    sh.write("rerun_shared_arm_manifest.json", expect=len(BASES) * len(TAGS) * 2)
    ds.write("rerun_downstream_cond_manifest.json", expect=len(BASES) * 2 * 2 * len(BENCH))
    cells = {c["name"]: c for c in sh.cells + ds.cells}
    smoke = [cells["llama31_8b__rds_l0__seed2"], cells["llama31_8b__l0_humaneval__indep1"]]
    (CFG / "rerun_lost_smoke_manifest.json").write_text(json.dumps(smoke, indent=1))
    rest = [c for c in sh.cells + ds.cells if c not in smoke]
    (CFG / "rerun_lost_manifest.json").write_text(json.dumps(smoke + rest, indent=1))
    print(f"wrote rerun_lost_smoke_manifest.json (2) and rerun_lost_manifest.json "
          f"({len(smoke) + len(rest)}, smoke cells first)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
