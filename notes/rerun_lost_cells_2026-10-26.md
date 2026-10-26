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

## Result of the re-run (2026-10-27), and an unregistered follow-up

All 88 cells landed (PBS 12863 to 12867, no failures). Both tests land in the
published branch, **CONFIRMED**, under their original rules and analyzers.

- Shared arm: P1 and P2 hold on 4 of 4. lambda = 0 ratios 4.30, 66.0, 9.42,
  2.46 (published 4.42, 76.2, 10.8, 2.82); P2 gates 0.019, 0.465, 0.049,
  0.149 (published 0.024, 4.26, 0.128, 0.166); seed1 sits 0.11, 0.92, 1.14,
  0.41 sd from its arm's mean (published 0.23, 0.53, 0.75, 0.66), all under
  the registered 2.
- Downstream: GSM8K P1 4/4, P2 4/4; HumanEval P1 3/4 (published 4/4; Yi
  misses by 0.001), P2 2/4 (published 3/4; Mistral misses by 0.005). Mistral
  shared lambda = 0 is 0.000 on both benchmarks again, recovering to 0.460 and
  0.232 (published 0.462, 0.244).

**The re-run does not reproduce the lost lambda = 0 values on the shared
arm.** From the published ratios and the (reused, unchanged) seed1 and
independent cells, the lost seed2 + seed3 sums at lambda = 0 were 0.636,
25.38, 0.648 and 0.789 (Llama, Mistral, Qwen, Yi); the re-run gives 0.611,
20.67, 0.540 and 0.657. Lower on all four, by 4% to 19%; on Mistral the lost
cohorts were about 16 and 9.4 nats, against 10.58 and 10.09 now. This is far
outside the float32 scatter measured on seed1 (Mistral range 0.08 nats).

What was checked: the re-run's nll_tau equals, bit for bit, the nll_tau that
June and September cells computed in-cell from the original adapters, on all
four bases and both cohorts (`eval_seed_rdridge_regmean`, `eval_ridge_seed`,
`eval_regmean_real`). The adapters and evaluation data are therefore the
same, and the difference is in the merge. The float32 encoder at lambda = 0
on shared cohorts depends on the random stream of its randomised SVD
(`notes/check_solve_precision_result_2026-10-24.md`); even the 2026-10-24
repeat of an August Yi seed1 cell matched in worst-task excess (0.2489 vs
0.2490) but not in average excess (0.1585 vs 0.1643), so the stream differs
between runs. The scatter has been measured on seed1 only.

**Follow-up, unregistered, written before its cells.** The seed1 sweep of the
precision note, repeated on seed2 and seed3: for each base and cohort, the
re-run cell `eval_ridge_shared/<base>__rds_l0__<cohort>` with `rng_seed` 1
and 2 added, float32, production truncation, everything else unchanged; 16
cells named `<base>__rd_l0_rerun_s<k>__<cohort>` in `eval_precision_f64/`,
same nll_tau cache. Reading fixed now:

1. Per base and cohort, the three draws (re-run default, s1, s2) and their
   range are reported, with whether every draw is above that base's
   independent mean.
2. Per base, the nine seed2 + seed3 sums formed from the draws are compared
   with the lost sum above. If the lost sum lies inside their range, the
   manuscript says the lost value is within the float32 scatter of the
   re-run. If it lies outside, the manuscript says the re-run did not
   reproduce it, gives both, and says the cause cannot be established because
   the lost files are gone.
3. Whether every combination keeps the shared-over-independent ratio at or
   above 2 is reported. It does not change the verdict, which comes from the
   registered cells.
4. The manuscript gives the shared-arm ratios from the registered re-run
   cells, not from any mixture of draws.

## Follow-up result (2026-10-27, PBS 12939 to 12942)

`python code/phase3/scripts/summarize_precision_sweep.py --sweep23`; nll_tau
and rng_seed asserted per cell. Worst-task excess at lambda = 0, float32,
production truncation (default = the registered re-run cell):

| base | seed2 default / s1 / s2 (range) | seed3 default / s1 / s2 (range) | indep mean | lost sum | sums over draws | ratio over draws |
|---|---|---|---|---|---|---|
| Llama | 0.2890 / 0.2944 / 0.3218 (0.033) | 0.3217 / 0.3803 / 0.4003 (0.079) | 0.0712 | 0.636 | 0.611 to 0.722 | 4.30 to 4.83 |
| Mistral | 10.579 / 9.467 / 10.476 (1.112) | 10.095 / 10.997 / 10.113 (0.903) | 0.1537 | 25.38 | 19.56 to 21.58 | 63.6 to 68.0 |
| Qwen | 0.2763 / 0.2583 / 0.2464 (0.030) | 0.2635 / 0.2868 / 0.4139 (0.150) | 0.0261 | 0.648 | 0.510 to 0.690 | 9.04 to 11.35 |
| Yi | 0.2082 / 0.2000 / 0.2528 (0.053) | 0.4489 / 0.4574 / 0.2267 (0.231) | 0.1227 | 0.789 | 0.427 to 0.710 | 1.84 to 2.61 |

Reading, as fixed before the cells:

1. Every draw on every base and cohort is above that base's independent
   mean. The scatter is larger than the seed1 sweep showed: ranges of 0.03 to
   0.23 nats on Llama, Qwen and Yi, and 0.9 to 1.1 nats on Mistral, whose
   excess is about 10 nats.
2. On Llama and Qwen the lost sum lies inside the range of the draws, so the
   manuscript says the lost values are within the float32 scatter of the
   re-run. On Mistral and Yi it lies outside, so the manuscript says the
   re-run did not reproduce them, gives both, and says the cause cannot be
   established because the lost files are gone.
3. Not every combination keeps the ratio at or above 2: on Yi the draws give
   1.84 to 2.61. The registered verdict is unchanged (the registered cells
   give 2.46), and the manuscript reports that on Yi the factor of two in P2
   depends on the random stream.
4. The manuscript's ratios are those of the registered re-run cells: 4.3,
   66, 9.4 and 2.5.
