# Re-run of two lost tests: the shared arm at n = 3 and downstream conditioning

Written 2026-10-26, **before the generator for these cells exists** and before
any cell is dispatched. The commit ordering is the evidence.

## Why

The per-cell files and summaries of two registered tests were never committed
and were lost when the cluster tree that held them was emptied on 2026-10-10:

1. **The ridge sweep's shared arm at n = 3** (`eval_ridge_shared`,
   `shared_arm_summary.json`): 56 NLL cells, registered in
   `notes/prereg_shared_arm_2026-08-15.md` (603e013).
2. **Downstream accuracy on the conditioning collapse**
   (`eval_downstream_cond`, `downstream_conditioning_summary.json`): 32
   accuracy cells, registered in `notes/prereg_downstream_2026-08-15.md`
   (df832fe) and amended by `notes/prereg_downstream_amendment_2026-08-15.md`
   (4d48987).

Their numbers survive only in the committed text of the JAIR version
(`paper/sections/method_tests.tex`), and the Neurocomputing manuscript cites
them (Section 6, Table 3). `notes/claims_ledger_2026-10-26.md` lists them as
backing gaps. The user chose on 2026-10-26 to re-run the cells rather than
disclose the loss or restate the claims.

## What governs the re-run

The two registrations and the amendment above, **unchanged**. No threshold,
gate, prediction, decision rule or consequence text is restated here, and none
may be changed. The verdicts are computed by the committed analyzers,
`analyze_shared_arm.py` and `analyze_downstream_conditioning.py`, unchanged,
run with `RDMERGE_ROOT` pointing at the student-account tree.

## What differs from the August run

- **Configurations.** The original per-cell YAML files were lost with the
  tree. The generator rebuilds them from the template the originals used,
  `eval_a1_indep/<base>__rd_ridge__indep1`, read from the configuration
  embedded in that published result file. It keeps every invariance check of
  the two original generators (`gen_shared_arm.py`,
  `gen_downstream_conditioning.py`): the new cells must equal the published
  seed1 NLL cells at the same lambda field for field, the two cohorts of a
  pair may differ only in the adapter directory, and the evaluation sizes are
  the amended ones. lambda* is read from the published `eval_ridge_cond`
  cells, as before.
- **Models and adapters** are the re-staged copies under the student account,
  the same copies the October campaign used.
- **Code** is the current tree. Since the August run, the encoder gained
  options whose defaults leave the production merge unchanged (51bebb5), and
  the downstream harness gained two self-loading metrics; the GSM8K and
  HumanEval scorers are unchanged since 2026-08-15. On 2026-10-24 the
  production configuration re-run on the re-staged models gave 0.2489 on the
  one August cell it repeated (published 0.2490,
  `notes/check_solve_precision_result_2026-10-24.md`).
- **nll_tau** comes from `nll_tau_cache_v2/<base>__<cohort>.json`. Its seed2
  and seed3 entries carry the same key as the seed1 entries (evaluation seed
  20260518, 1,000 examples per task, maximum length 1024, plain loader), and
  the seed1 entries equal the published cells' nll_tau exactly on all four
  bases (checked 2026-10-26). The harness refuses any cache entry whose key
  differs.
- The seed1, indep1, indep2 and indep3 NLL cells are the published ones,
  reused and not re-run, as both registrations require.

## Blindness

**Not blind.** We know the published verdicts and numbers. Both tests were
CONFIRMED. The shared arm gave lambda = 0 ratios of 4.42, 76.2, 10.8 and 2.82
(Llama, Mistral, Qwen, Yi) against gates of 0.024, 4.26, 0.128 and 0.166, and
seed1 sat 0.23, 0.53, 0.75 and 0.66 sd from its arm's mean. The downstream
test gave the 16-row table `tab:downstream-cond`, including Mistral's
shared-cohort 0.000 on both benchmarks, recovering to 0.462 (GSM8K) and 0.244
(HumanEval) at lambda*.

None of the 88 new cells' values is known. We also know that the float32
encoder at lambda = 0 on shared cohorts moves by 0.02 to 0.08 nats between
random draws, so the re-run need not reproduce the lost values exactly.

## What we report, fixed now

1. The re-run values **replace** the lost ones in the manuscript (Section 6,
   Table 3 and anywhere else they appear), whatever they are. The lost values
   are not kept alongside them as though both were current.
2. The verdict branch each test lands in under its original rules is
   reported. If it differs from the published branch, the manuscript says so,
   names the superseded verdict and its date, and writes the consequence text
   the registration fixed for the new branch. This is binding constraint 7 of
   the shared-arm registration and 6 of the downstream one.
3. The manuscript says these cells were re-run in October 2026 after their
   files were lost, and gives the agreement with the published values: per
   base, the re-run lambda = 0 ratio next to the published one, and the largest
   absolute difference over the 32 accuracies. It does this whatever the
   agreement is. We do not call a difference "within noise" in the manuscript
   unless it is smaller than the measured float32 scatter of that base, and we
   give the scatter alongside.
4. Everything the registrations list under "reported regardless of outcome".

## Procedure

1. This note is committed first. The generator (`gen_rerun_lost.py`) and the
   smoke check are committed second. Then the code is deployed and the cells
   are generated on the cluster.
2. **Smoke cells first**, as both registrations require: one NLL cell
   (`llama31_8b__rds_l0__seed2`, the shared arm's original smoke candidate)
   and one accuracy cell (`llama31_8b__l0_humaneval__indep1`, the downstream
   test's). They are inspected for configuration equality, a cache hit on
   nll_tau, a merge that is not a no-op and a non-zero scorer yield. The check
   prints none of the values that decide a verdict. Blindness to the new
   values is then 55 of 56 and 31 of 32, as in August.
3. The remaining 86 cells are dispatched on `STUDENT-ACCOUNT` only, never GPU 7,
   with walltime successors. No partial reads: the analyzers refuse to report
   until every cell exists.
4. The per-cell files and both summaries are copied down and **committed**
   this time.
