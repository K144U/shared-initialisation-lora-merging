# Claims ledger, Neurocomputing manuscript (2026-10-26)

Every number in the main text (sections 1 to 8, the abstract and Appendix D)
was checked against the file it comes from, recomputed from per-cell results,
or traced to a committed verdict note. Rounding is checked at the displayed
precision. Paths are relative to the repository root; "R" is
`results/phase3`. Where a value is read from a per-cell folder that is not in
the repository, the folder is named and marked *(cluster only)* or *(local,
untracked)*.

Outcome: eight errors found and fixed in efcaf99 (listed at the end); two
claims whose per-cell evidence no longer exists anywhere we can reach (see
"Backing gaps"); everything else verified.

## References (38 cited)

All 38 checked for title, authors, venue, year, volume and pages against
arXiv (export API), PMLR, OpenReview, OpenAlex/Crossref and the ACL
Anthology. Fixed: Fisher merging (inproceedings, NeurIPS 35, pp. 17703 to
17716); Unsloth credited to the authors its README names. What each cited
paper is said to do was checked against its abstract or text; the three
non-obvious ones were read in the paper itself: Cao et al. prove a bound for
convex merges (Thm., "no convex merging method can achieve distortion
below"), the systematic study finds only task arithmetic reliably improves on
the base model across four open-weight LLMs, Core Space "uses the exact LoRA
checkpoints" released by KnOTS, ZipLoRA observes that highly aligned columns
merge poorly.

## Section 3

| Claim | Source |
|---|---|
| NLL drops 10 to 70% on own task (3 adapters) | `nll_tau` in any per-cell file, e.g. R/eval_regimes, R/eval_a1_indep: 10% (Yi, Alpaca) to 69% (Qwen, GSM8K) |
| translation adapter beaten at translation on every base | R/campaign_2026-10/all_tasks_summary.json `reference_rows` (base beats it on 3, Alpaca adapter on Yi) |
| drift 0.1308 / 0.1303, cosines 0.996 / 0.048 | R/drift_summary.json `arms` |
| seed table (all 13 values) | R/campaign_2026-10/training_regimes_summary.json `S` |
| regimes table, median cosine | R/geometry_T4_vs_T3.json |
| regimes table, mean kappa and amplification | R/floor_conditioning.json `seed1 | T=4 (all)`, `indep1 | T=4 (all)` |
| 9,216 cosines, min 0.75 / max 0.18, singular values | paper/nc/data/geometry_stats.json (4 x 3 x 768 per arm) |
| T and r sweep (12 values) | R/campaign_2026-09/new_cohorts_summary.json `R.geometry` |
| seven training changes, 0.956 to 0.999, indep 0.047 / 0.048 | R/campaign_2026-10/training_regimes_summary.json `K.geometry`, `K.indep` |
| PiSSA 0.999, 0.9996 | new_cohorts_summary.json `P` |
| libraries 1.000, 0.9996, 0.9994 | training_regimes_summary.json `L` |
| continued training 0.997, 2.9e4, 1.49 | training_regimes_summary.json `C` |
| DoRA 0.995 / 0.047 | training_regimes_summary.json `D` |
| vision cohorts 0.96 / 0.11 | R/campaign_2026-10/vision_summary.json `geometry` |

## Section 4

| Claim | Source |
|---|---|
| 21 kappa ratios in [0.9990, 1.0005] | R/campaign_2026-09/drift_theory.json `pt4` (12) and `checkpoints` (4), new_cohorts_summary.json `R.geometry` (5); extremes 0.998991, 1.000547 |
| slopes -2.00 / -1.01, five s from 0.05 to 1 | drift_theory.json `dial` |
| kappa 2.7e4 to 1.1e4, amplification 61 to 44 | drift_theory.json `checkpoints` |
| isotropic 13% gives 5e2, low-rank 1e5 to 1e6, within 0.3% | code/phase3/scripts/drift_theory_synthetic.py, rerun 2026-10-26: 5.22e2, 7.76e5, ratios 0.997 to 1.000 |
| out-of-sample law: 8/8, 7/8, Spearman -0.976, t* 22, 27x, 0.83 | training_regimes_summary.json `K` |
| RegMean excess 0.34, 0.38 vs 0.057, 0.073; 0.022 on A0 x 0.25 | R/eval_regimes/llama31_8b__rm1em6__{k_lr3,k_amult4,ki_lr3,ki_amult4,k_scale025}.json *(local, untracked)*; also notes/campaign_2026-10-19_redteam.md |
| amplification 7.5 vs law 13.7; lr x 3 amplification 15.9 | training_regimes_summary.json `K.geometry`, `K.pred` |

## Section 5

| Claim | Source |
|---|---|
| partial collapse cohorts (16 values) | R/campaign_2026-10/heterogeneity_summary.json `M` |
| 1000 walked, 50 cohorts, 45 scored, 17 collapsed, 37.8% | paper/nc/data/prevalence_summary.json |
| 27 separated at 0.076, one at 0.868 | same file, cohort statuses |
| distance 1.414 separated (25 with a distance; two differ in rank), 0.017 to 0.760 collapsed, one at 0.29 | same file `rel_A_diff` |
| re-read: 40 readable, error 0.003, 18/45, 0.064 / 0.998, 0.440 / 0.717 | R/campaign_2026-10/prevalence_maxpair.json; notes/campaign_2026-10-19_redteam.md |
| the 18 classified (1, 1, 4, 3, 9; 6 tasks, 12 versions; LoRAHub 196, 16 writing styles) | R/campaign_2026-10/collapsed_cohort_classes.json, collapsed_cohort_metadata.json |
| KnOTS 0.968, 0.110, 0.095 | R/campaign_2026-09/prevalence_part_b_prevalence_summary.json |
| library code (Unsloth 3407, LLaMA-Factory 42, PEFT) | source read at pinned versions, notes/campaign_2026-10-19_redteam.md Part L |

## Section 6

| Claim | Source |
|---|---|
| WUDI table, all 12 ratios and 32 accuracies, gates | R/campaign_2026-10/wudi_summary.json |
| WUDI tail 0.03 to 0.17 (closed form), amplification 8.6 to 12.5, off-range 24 to 27% | wudi_summary.json |
| WUDI independent tail 0.29 to 0.35, off-range 0.8 to 1.6% | R/eval_wudi `merge_diagnostics` *(cluster only)*, read 2026-10-26 |
| energy: 0.98 to 2.16, tail < 0.001, 35 to 57, 73 to 80%, independent 0.20 to 0.32 | R/merged_solution_norms.json |
| heuristics NLL: 15 of 20, five past gate, three KnOTS, largest 0.015 | recomputed 2026-10-26 from R/eval_matrix_seeds, R/eval_a1_indep, R/eval_a2_knots_ties{,_indep} *(local, untracked)* |
| TOST margins, 0.9 to 2.0 and 2.1 to 3.0, TIES Llama 6.5 | R/campaign_2026-09/heur_tost_summary.json |
| sign test 29 / 38, p = 0.0017 | heur_tost_summary.json `sign` |
| permutation p = 0.007, lean 0.7, all bases | R/campaign_2026-10/heuristics_cohort_permutation.json |
| truncation 12 to 25% vs 1.3 to 1.6%, not halved | R/campaign_2026-10/untruncated_summary.json `H1`, `H2` |
| activation-Gram RegMean 0.99 to 1.14, 8/8, 1.3 points | R/campaign_2026-09/regmean_real_summary.json `Q1`, `downstream.table` |
| most accurate on three of four bases (two-benchmark mean) | regmean_real_summary.json, heur_tost_summary.json, third_solver_summary.json |
| MaTS 0.93 to 0.99, Mistral GSM8K; Fisher 0.96 to 1.08; TSV-M 0.81 to 1.19 | R/campaign_2026-09/third_solver_summary.json |
| adapter-only RegMean 4.1, 65.6, 5.8, 1.8 | R/campaign_2026-09/regmean_agram_summary.json `described_gram_AtA` |
| shipped-alpha accuracy 0.168 ... 0.724; ridge +31, +43, +54; Mistral 0.029 / 0.002 | regmean_real_summary.json `downstream` |
| encoder 2.5 to 66, three cohorts per arm | R/shared_arm_summary.json (re-run 2026-10-27, a8cdc02): 4.30, 66.04, 9.42, 2.46 |
| encoder Mistral 0.000, recovering to 0.46 / 0.23 | R/downstream_conditioning_summary.json (re-run, a8cdc02): 0.000, 0.460, 0.232 |
| encoder untruncated 25 to 117 | R/eval_ridge_untrunc *(local, untracked)*: 116.9, 73.5, 35.2, 25.5 |
| selected lambda equal on 3 of 4 (encoder) | R/eval_ridge_cond *(local, untracked)* |
| float64 check: 0.1%, 15 of 16, 0.9%, 1.09%, truncation 98.8 to 99.9%, 30 to 38%, 12 to 20% | R/campaign_2026-10/solve_precision.json |
| draws: 36 above independent; spans 0.08 / 0.15 / 0.23 / 1.1; Yi seed3 0.23 vs 0.10; Yi ratio 1.8 to 2.6 | summarize_precision_sweep.py (and --sweep23), R/eval_precision_f64, R/eval_ridge_shared (c72df0f) |
| App. B re-run: ratios vs lost; accuracies within 0.024 except shared lambda = 0 up to 0.106; identical merge 0.022; HumanEval misses 0.001, 0.005 | notes/rerun_lost_cells_2026-10-26.md; downstream_conditioning_summary.json vs JAIR tab:downstream-cond |
| rebuild 0.245 / 0.249 / 0.121; draws 0.22 to 0.28, 0.26 to 0.84; other bases' draws | notes/check_solve_precision_result_2026-10-24.md; Appendix C tables (make_app_campaign.py asserts against R/eval_precision_f64) |
| alpha equivalence 5.8e-4 to 6.8e-4, 0.5%, kappa 1.2e3 to 1.4e3, 6.6e3 to 9.1e3, 1.5e2 | R/regmean_published_default.json (alpha_equiv_ridge_median / 0.9) |
| vision, all 17 values | R/campaign_2026-10/vision_summary.json |
| all tasks: chrF and IFEval gains, gates, 1.1, 0.057, 0.627 / 0.703 | R/campaign_2026-10/all_tasks_summary.json |
| lambda rules: 4/6, 2/6, 1/6 | R/campaign_2026-09/public_merge_public_merge_summary.json (`V4`, `U2`); notes/campaign_2026-09-28_final_verdicts.md |
| GCV and L-curve (1.13, 8.66, 0.22, 0.45 on the first shared cohort; 1.3e-8) | R/campaign_2026-10/lambda_selection_summary.json |
| public merges 5/6, 11/13, p = 0.78, one unloaded | public_merge_public_merge_summary.json |
| heterogeneity 4%, 3.9, 5.3, 0.26, 0.29, norm spread | heterogeneity_summary.json `G`, `G4_medians` |

## Section 7

| Claim | Source |
|---|---|
| activation-Gram amplification 2.2 to 6.5, kappa to 1e7 | regmean_real_summary.json `Q1m_amp_shared`; notes/campaign_2026-09-23_strengthen.md |
| encoder vs best baseline 1 win, 1 tie, 2 losses; none after controls | notes/campaign_results_2026-08-03.md (verbatim analyzer output); paper/sections/method_tests.tex (JAIR) |
| overlap 13 to 16% and 9 to 12% | R/r5_disjoint_summary.json `masks` |
| ordering unchanged in 23 of 24 rows | R/r5_disjoint_summary.json `cells` (recounted 2026-10-26) |

## Backing gaps

**Update 2026-10-27: gaps 1 and 2 are closed.** All 88 cells were re-run under the
original registrations (note b9d0e41, generator d77cd8c, results a8cdc02); both tests
are CONFIRMED again. The values moved (see notes/rerun_lost_cells_2026-10-26.md and
Appendix B), and the manuscript now gives the re-run values. The text below records
the state on 2026-10-26.

Two sets of per-cell files were lost when the cluster tree that held them was
emptied on 2026-10-10. Their numbers survive only in
the committed text of the JAIR version, which is in the public history.

1. **Encoder at lambda = 0, shared seeds 2 and 3** (`eval_ridge_shared`,
   `shared_arm_summary.json`). Section 6 and Table 3 give "2.8 to 76 times,
   three cohorts per arm". Source: JAIR `method_tests.tex`, subsection
   "shared arm at n = 3": ratios 4.42, 76.2, 10.8, 2.82, gates 0.024, 4.26,
   0.128, 0.166 (registration notes/prereg_shared_arm_2026-08-15.md). With the
   files that still exist (seed 1 against three independent cohorts) the
   ratios are 4.3, 63.6, 7.6, 2.0.
2. **Encoder accuracy with the repaired scorers** (`eval_downstream_cond`,
   `downstream_conditioning_summary.json`). Section 6 and Table 3 give
   "Mistral 0.000 on both, recovering to 0.46 and 0.24". Source: JAIR
   `method_tests.tex`, table `tab:downstream-cond`.

Options: re-run the lost cells (about 56 NLL cells and 32 downstream cells,
roughly 40 GPU-hours), or keep the numbers and say in Appendix B or D that
their per-cell files were lost, or restate the first claim from the surviving
seed-1 files.

A third gap is one of publication, not loss: the manuscript says the per-cell
results are public, but most October per-cell folders (R/eval_wudi,
R/eval_regimes, R/eval_all_tasks and others) are untracked locally or exist
only on the cluster. Committing them makes the statement true.

## Errors found and fixed (efcaf99)

1. s3: drift cohort independent cosine 0.047 -> 0.048 (0.0475257).
2. s4: "13% in every direction would give kappa ~ 60" dropped a factor of T;
   replaced by the synthetic result (5.2e2) the paragraph already cited.
3. s6: activation-Gram RegMean "most accurate on every base" -> on three of
   four (on Qwen, TSV-M, TVQ, TIES and MaTS are higher).
4. s6: heuristic tail "rounds to 0.000" -> "less than 0.001" (max 0.0007).
5. s6: independent tail range 0.19 -> 0.20 (min 0.195).
6. Fig. 4 caption: encoder "at its selected lambda" -> lambda = 0.05.
7. s6: GCV excesses are those of the first shared cohort of each base.
8. s7: disjoint ordering "19 of 20" -> "23 of 24". The analyzer divided 144
   cells by 7 methods; its denominator is fixed.
Also: abstract and Fig. 5 now say the ridge recovers most of the lost
*GSM8K* accuracy on three bases (on HumanEval only two).
