# Code provenance

This file records the origin of the main analysis components in the repository. It separates pre-existing research context, reused analysis modules, and CopyCAT-specific implementation work.

## Prior research context

The author's earlier GRIT / IEEE ICA 2026 work already developed refinement-invariance motivation, shared-partition certificates, additive/mergeable closures, and a tractability boundary for a different partition problem. Those ideas predate CopyCAT and are treated as prior work rather than new contributions here.

FActScore, FaStFact, MedQA, and MMLU-ProX data/model outputs are third-party public releases. Their exact sources and hashes are listed in `DATA.md`.

## Reused secondary-analysis modules

The following modules originated in earlier iterations of the same research program and were rerun for the final CopyCAT analysis:

`analyze_factscore.py`, `analyze_fastfact_prospective.py`, `conjunction_identity.py`, `factscore_matched_control.py`, `medqa_crossmetric.py`, `natural_controls.py`, `natural_counts.py`, `refinement.py`, `reproduce_medqa.py`, `robustness_audit.py`, `verifier_check.py`, `verify_weighted_repair.py`, and `weighted_measure.py`.

The factuality and natural-count analyses are exploratory. Reused labels or verifier outputs are not described as unseen-data confirmation.

## CopyCAT-specific implementation

| File | Role |
|---|---|
| `code/mmlu_release.py` | pinned acquisition, integrity/alignment checks, exact rational pairwise audit, full pairwise matrices |
| `code/test_mmlu_exact.py` | exhaustive subset/budget checks and arithmetic regressions |
| `code/joint_winners.py` | shared-schedule joint unique-winner optimization and certificate validation |
| `code/test_joint_winners.py` | independent brute-force verification of small joint problems |
| `code/reproduce_headline.py` | standard-library reproduction of the compact headline certificate |
| `code/verify_results.py` | consistency checks across the compact derived result files |
| `code/acquire_sources.py` | public-source acquisition and hash verification |

The MMLU implementation uses exact integer/rational comparisons for the certificate calculations. Feasible joint witnesses are recomputed in integer arithmetic, and the headline exclusions are accompanied by blocking-rival integer certificates.

## Development notes

Earlier development versions contained a 583-question denominator, compared numerators across variable denominators, and over-escaped a filename regex. The current implementation uses the complete 588-question aligned archive and includes regression tests for those failure modes.

General reweighting sensitivity, mass conservation, weighted metrics, and election-control complexity are not treated as novel results of this repository.
