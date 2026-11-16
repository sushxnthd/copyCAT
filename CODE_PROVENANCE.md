# Code provenance

This record distinguishes pre-sprint intellectual prior work, earlier sprint campaign imports and code authored in the final revision. Import time is not first creation time. We do not infer independent timestamps from filenames, modification times or a protocol hash.

## Pre-sprint material

The author's GRIT / IEEE ICA 2026 manuscript, inspected source dated 31 October 2026, already presents refinement invariance, exact shared-partition certificates, witnesses/abstention, additive/mergeable closures and a tractability boundary for a different partition problem. These are preexisting motivation and are explicitly disclosed in the report. No GRIT repository/source file was imported directly during this final revision.

Public FActScore, FaStFact, MedQA and MMLU-ProX data/model outputs are third-party prior work. The sprint did not generate those releases. The original official report template is retained as `report/official_template_original.docx`; `report/template.docx` is the earlier populated derivative used by the builder. The template was downloaded directly from the official linked Google document and its footnote/theme were compared with the derivative.

## Imported earlier sprint campaign code

The following files were imported from the supplied earlier sprint reproducibility package, rather than claimed as newly written in this final revision. Its records attribute the analyses to the November 13–16 sprint campaign; their first authorship timestamps are not independently established here. All modules needed for reported results were computationally rerun.

`analyze_factscore.py`, `analyze_fastfact_prospective.py`, `audit_fastfact_integrity.py`, `conjunction_identity.py`, `factscore_matched_control.py`, `medqa_crossmetric.py`, `natural_controls.py`, `natural_counts.py`, `refinement.py`, `reproduce_all.py`, `reproduce_factscore.py`, `reproduce_medqa.py`, `robustness_audit.py`, `test_audit.py`, `test_refinement.py`, `verifier_check.py`, `verify_weighted_repair.py`, `weighted_measure.py`.

Associated protocols and historical saved outputs were imported and are marked as such. Earlier target-label and second-verifier access prevents describing these checks as unseen-data preregistered confirmation. The FaStFact protocol hash identifies the rule's content, not an external timestamp.

## Final revision code

Written during this revision on 16 November 2026 before the sprint deadline:

| File | Contribution |
|---|---|
| `code/mmlu_release.py` | Replaces the broken patch implementation; complete pinned acquisition, exact rational ratio optimization, integrity/alignment checks, full pairwise matrices and attained witnesses |
| `code/test_mmlu_exact.py` | Independent exhaustive subset/budget verification and ratio/regex regressions |
| `code/joint_winners.py` | Shared-schedule integer optimization, witness validation, integer blocking certificates, random controls and full budget curves |
| `code/test_joint_winners.py` | Independent brute-force verification of 680 tiny joint problems and incompatible-pairwise-witness regression |
| `code/verify_medqa_rational.py` | Exact fractions of released decimal confidence strings, independent endpoint/threshold checks |
| `code/acquire_sources.py` | Public-source downloader with original archive and per-file hash verification |
| `code/quick_demo.py`, `code/run_submission.py` | Standard-library headline verification and full ordered reproduction runner |
| `report/build_final.py`, `report/make_figures_final.py` | Revised official-template report and exact data figures |

No unsupported claim of first-ever general reweighting certification, mass conservation, weighted AUROC or election-control complexity is made. The joint-winner restriction and empirical result are explained with their closest known precedents in the report.
