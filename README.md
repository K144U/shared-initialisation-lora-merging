# When LoRA Adapters Share an Initialisation

Code, pre-registrations, per-cell experimental results and the manuscript for
*When LoRA Adapters Share an Initialisation: Subspace Collapse and Its
Consequences for Merging*, by **Sankalp Pathak**, **Sanjay Garg** and **Piyush
Kumar Singh** (Department of Computer Science and Engineering, Jaypee
University of Engineering and Technology, Guna). The manuscript is being
prepared for journal submission; its source is `paper/neurocomputing.tex`, with
the sections and appendices in `paper/nc/`.

This repository exists to be **checked**, not just read. Every confirmatory
test in the paper is governed by a pre-registration that was committed to
version control before the compute it governs was dispatched. The commit graph here is
intact, so that ordering can be verified with `git merge-base` rather than
taken on trust.

## Contents

- [One minute: check the trail yourself](#one-minute-check-the-trail-yourself)
- [What the paper claims](#what-the-paper-claims)
- [What did not survive](#what-did-not-survive)
- [Checking the audit trail in full](#checking-the-audit-trail-in-full)
- [What is not in this repository](#what-is-not-in-this-repository)
- [Repository layout](#repository-layout)
- [Reproducing](#reproducing)
- [Compute footprint](#compute-footprint)
- [Citation](#citation)
- [License](#license)

## One minute: check the trail yourself

The claim is that the rules were fixed before the results were in. Clone this
repository and test one row of it:

```
git clone https://github.com/K144U/shared-initialisation-lora-merging.git
cd shared-initialisation-lora-merging

# fff1699 fixed the rules for the WUDI-Merging test; c55e5d9 carries its result.
git merge-base --is-ancestor fff1699 c55e5d9 ; echo "exit $?"   # 0: rules came first
git merge-base --is-ancestor c55e5d9 fff1699 ; echo "exit $?"   # 1: and not the reverse
```

The first exits `0`, the second does not. That asymmetry is the whole claim,
and it holds for every row of the commit-ordering table in the manuscript's
pre-registration appendix. There is a script that checks every row and every
hash the table cites at once:

```
python code/phase3/scripts/verify_commit_table.py . paper/nc/app_prereg.tex
```

## What the paper claims

This section summarises the manuscript.

LoRA factorises each update as `BA`, draws `A` at random and starts `B` at
zero. Whether the `T` adapters of a cohort drew **one** `A` or `T` independent
ones is almost never reported, and a single global training seed, or the
default settings of Unsloth and LLaMA-Factory, silently decides it. Sharing the
draw leaves the tasks in nearly the same input subspace: across four base
models the median principal cosine between task row spaces moves from about
0.05 to above 0.99.

1. **A published data-free merge breaks.** WUDI-Merging, run exactly as its
   authors run it, leaves a worst-task loss excess 4.7 to 47.6 times larger on
   collapsed cohorts than on independent ones, on all four base models; on
   GSM8K it scores 0.03 against 0.70 on Llama-3.1-8B. We had registered the
   opposite prediction, that its early-stopped optimiser would protect it.
2. **The consequence splits cleanly by method.** The collapse breaks the merges
   that solve a least-squares problem built from the adapters alone: WUDI, a
   data-free form of RegMean, and our own closed-form encoder, which on
   Mistral-7B scores **zero** on both GSM8K and HumanEval. Averaging and
   sparsifying merges are equivalent across the two regimes within 3 accuracy
   points on GSM8K and 5 on HumanEval, and solvers built from data (RegMean
   with activation Grams, MaTS) or a diagonal one are unaffected.
3. **A one-CPU-minute audit.** The collapse is measurable from the adapters'
   `A` factors alone: no forward passes, no evaluation data, no merging. Under a
   sampling frame fixed before any download, it finds at least **18 of 45**
   public LoRA cohorts collapsed.
4. **A first-order theory.** Treating each adapter's `A` as a small
   displacement of the shared start accounts for the conditioning of the merge
   operator within 0.10% in 21 configurations, and a scalar law derived from
   it predicts the condition number of eight cohorts trained afterwards within
   a factor of 2.

Regularising a least-squares solve is standard practice, so we checked what the
standard practice actually does. On the adapter Grams, RegMean's shipped
alpha-shrinkage default of 0.9 has the average size of a ridge of about 6e-4,
more than ten times smaller than the `lambda = 0.01` that repairs most of the
damage on three of four bases, and it leaves a collapsed cohort's system at
condition number 6.6e3 to 9.1e3 against about 1.5e2 with that ridge. It applies
the same dose on a well-conditioned cohort, where it is ample. **The default
regularisation does not know which regime it is in, and the audit is what tells
you.**

## What did not survive

Several pre-registered tests went against us, and several things had to be
fixed or re-run. They are here for the same reason the paper reports its
failed predictions.

- **WUDI was predicted to be protected by its optimiser, and it is not.** That
  failed prediction is now the paper's lead result.
- **No data-free rule sets the ridge.** A condition-number target,
  generalised cross-validation and the L-curve all failed their registered
  criteria; the paper recommends starting at 0.01 and sweeping on held-out
  data.
- **Our encoder loses its advantage** in the move from shared-initialisation
  cohorts to properly initialised ones. The paper claims no win for it.
- **An earlier headline claim of ours is withdrawn and stays withdrawn**: that
  published merging benchmarks are confounded by initialisation geometry. A
  control we designed ourselves refuted it. A later margin-aware control would
  reinstate it, but that control was written after its data had been seen, and
  we do not use it that way.
- **The rate-distortion bound is provenance, not a contribution.** It is why we
  looked at the conditioning at all, and no more than that. Its floor term is
  exactly zero on every cohort we measured, its rate term rests on an
  assumption stated but not proved, and it derives none of the four results
  above. The rate exponent it predicts is **unresolved**: our sweep lacks the
  dynamic range to measure it.
- **One of our four adapters never learned its task.** Both arms contain the
  same weak member, so every comparison between them is matched.
- **The original scorers were broken.** The HumanEval extractor returned an
  empty completion for markdown-fenced output and the GSM8K extractor required
  the answer at end-of-string, discarding 61% to 81% of generations on some
  method and base combinations and near zero on others, which makes
  cross-method comparison meaningless. Both are fixed, all affected cells were
  re-scored, and the discard rate is now zero.
- **Training and evaluation splits are not disjoint** on two of the four tasks:
  12.9% to 16.2% overlap on the instruction-following task and 9.2% to 11.6% on
  the code task. Absolute numbers here are therefore optimistic and are not
  held-out performance. Whether that affects comparisons *between* methods was
  tested rather than asserted: on the disjoint subset the method ordering is
  unchanged in 23 of 24 base-by-cohort comparisons and the worst task is the
  same in all 144 cells.
- **Two registered tests were re-run after their files were lost.** The
  per-cell files of the shared arm at three cohorts and of the downstream
  accuracy test were lost before they were committed. All 88 cells were re-run
  under the original registrations, and both tests reach the same verdict. The
  values moved, and on Mistral-7B and Yi-1.5-9B the re-run does not reproduce
  the lost values at lambda = 0; the manuscript's pre-registration appendix
  compares the two runs.

## Checking the audit trail in full

The pre-registrations are in `notes/prereg_*.md`, unedited. Their stale
internal cross-references are deliberate: they are the evidence that nothing
was rewritten after the fact. The paper's appendix on pre-registration
documents and commit ordering lists, per row, the commit that fixed the rules
and the commit carrying the result they govern. For each row:

```
git merge-base --is-ancestor <rules-commit> <result-commit>
```

exits zero exactly when the ordering claimed holds, and fails on the reverse.

## What is not in this repository

The published history is **filtered** from a working repository, which rewrote
every commit hash, so the hashes here are this repository's rather than the
working one's. Filtering changes hashes but not the commit graph, and the graph
is what the verification above depends on. Four things are treated differently
from the rest, and none is cited anywhere in the paper or bears on any result.

Removed from **every** commit:

- Private correspondence and external review notes, which were never ours alone
  to publish.
- Large build artifacts, which would bloat the history without adding to it.
- Text identifying a manuscript still under anonymous review elsewhere.

Removed in the **final commit only**, and so still present if you check out an
earlier one:

- The project's working apparatus: session handoffs, the running log and
  decision journal, planning documents, prompt templates, the build files and
  submission packages of earlier versions of the manuscript, and early theorem
  drafts. None of it is secret and none
  of it is cited; it simply is not what a reader of the paper came for. It was
  dropped at the tip rather than scrubbed from history on purpose, because
  scrubbing would have changed every commit hash and broken the hashes the
  paper pins. Leaving the history intact matters more here than a tidy
  file listing.

Not redistributed at all:

- The base model weights and the trained adapters. The bases are public
  checkpoints, and the adapter training configurations, including every seed,
  are here.

## Repository layout

```
paper/                   LaTeX source
  neurocomputing.tex     the build root of the manuscript
  nc/                    its sections, appendices, figures, build.sh and
                         the scripts that generate its figures and tables
  prereg/                the August pre-registrations, as typeset
  preamble.tex
  references.bib
notes/prereg_*.md        the pre-registration documents
code/phase3/
  merging/               merge implementations: task_arithmetic, ties, dare,
                         dare_ties, della, knots, tvq, regmean, adamerging,
                         fisher_avg, magnitude_prune, rd_encoder
  eval/                  evaluation drivers, NLL excess and downstream accuracy
  training/              LoRA training pipeline
  scripts/               generators, analyzers, figure makers, PBS launchers,
                         and verify_commit_table.py
  configs/               per-cell YAML configs and orchestrator manifests
code/synthetic/          the synthetic overlap sweep
results/phase3/          per-cell JSON outputs and summary JSONs
```

## Reproducing

```
conda create -n rdmerge python=3.11 -y
conda activate rdmerge
pip install -r requirements.txt
export PYTHONNOUSERSITE=1
export RDMERGE_ROOT=$(pwd)
```

### The audit, which needs no GPU

This is the measurement the paper asks you to run first, and it is deliberately
cheap: CPU only, from adapter weight files, about a minute per cohort.

```
python code/phase3/scripts/measure_subspace_geometry.py --cohort seed1
python code/phase3/scripts/measure_subspace_geometry.py --cohort indep1
```

`seed1` is a shared-initialisation cohort and `indep1` an independently
initialised one. The paper's geometry and conditioning tables are built from
this script and its siblings `geometry_T4_vs_T3.py` and `floor_conditioning.py`,
so every number in them is reproducible without GPU access.

The prevalence study over public cohorts is `audit_public_cohorts.py`, which
runs its metadata phase and fixes every inclusion decision before downloading
any weights. The library-source condition under which two adapters receive
identical `A` factors is worked out in `audit_peft_init_condition.py`.

### A single evaluation cell

```
python code/phase3/eval/run_eval_cell.py --config code/phase3/configs/eval_matrix_seeds/llama31_8b__ties__seed1.yaml
```

Larger sweeps are driven from the manifests in `code/phase3/configs/*.json`
through the orchestrator, one worker per pinned GPU. Analyzers are
`code/phase3/scripts/analyze_*.py`, and each refuses to report until every cell
it needs exists. That is a pre-registration constraint, not a convenience.

### Rebuilding the paper

The manuscript needs `pdflatex`, BibTeX and Elsevier's CAS classes
(`els-cas-templates`, v2.4). `paper/nc/build.sh` expects the CAS bundle in
`paper/nc/NCTemplate/els-cas-templates/`, which is not redistributed here;
download it from Elsevier or CTAN and unpack it there.

```
cd paper && bash nc/build.sh --no-figs   # PDF only: paper/neurocomputing.pdf
```

## Compute footprint

All merging and evaluation ran on a single node with A100-80GB GPUs, one
evaluation cell per card at 18 to 21 GiB. Before its final campaign the project
trained 112 LoRA adapters and completed roughly 1,200 evaluation cells at 17 to
26 minutes each, on the order of **400 GPU-hours**. The final campaign trained
further adapters (the training regimes and routes of the manuscript's
Section 3, and small adapters for the vision experiment) and ran several
hundred more cells, which that count does not include. The totals include
superseded runs: these results were not obtained on the first attempt, and
several of the corrections above required re-running cells that had already
been analysed.

## Citation

The paper is not yet published, so there is no journal, volume, article number
or DOI yet.

```bibtex
@unpublished{pathak2026shared,
  title  = {When {LoRA} Adapters Share an Initialisation: Subspace Collapse
            and Its Consequences for Merging},
  author = {Pathak, Sankalp and Garg, Sanjay and Singh, Piyush Kumar},
  year   = {2026},
  note   = {Manuscript}
}
```

Our earlier preprint,
[10.5281/zenodo.21238820](https://doi.org/10.5281/zenodo.21238820), titled *A
Rate-Distortion Function for Model Merging*, proposed the closed-form encoder
that the manuscript tests as one of its merges. It predates the
pre-registered experiments reported here, and two of its claims do not hold up
in them: that its encoder has the lowest worst-task loss of the methods it
compared, an advantage that came from the shared initialisation of its cohorts,
and that worst-task NLL tracks the downstream ranking of methods. The
manuscript does not use its rate-distortion bound. For the results in this
repository, please cite the entry above.

## License

MIT, see [`LICENSE`](LICENSE).
