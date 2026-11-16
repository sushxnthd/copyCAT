# CopyCAT

Copy-Controlled Attainability Testing (CopyCAT) is a finite-archive audit for benchmark decisions under bounded duplication of existing evaluation units.

This repository contains the implementation, derived result files, source-integrity checks, and paper material for **CopyCAT: Exact Winner Certificates When One Fact Counts Twice**.

## Overview

The audit keeps model outputs and labels fixed. For aligned evaluation roots, each root may receive at most one additional copy, and the same copied-root schedule is applied to every compared system. Under that contract, CopyCAT computes:

- exact pairwise extrema at each copy budget;
- minimum-copy ties and strict reversals;
- joint unique-winner feasibility under one shared schedule;
- blocking certificates for systems that cannot become unique winners;
- mass-preserving checks for value-preserving refinements when root lineage is known.

The main MMLU-ProX-Lite analysis uses a pinned English archive with 588 aligned questions and 10 released configurations.

## Repository layout

```text
code/           algorithms, analyses, tests, and data-acquisition utilities
results/        compact derived results and exact certificates
verification/   stored reproduction/regression check summary
docs/           prior-work notes and the joint-winner proof
paper/          supplementary paper source and compiled PDF
examples/       minimal generic audit input
DATA.md         public data sources, pinned revisions, hashes, and local layout
CODE_PROVENANCE.md  development/provenance notes
```

## Environment

Python 3.12+ is recommended.

```bash
python -m pip install -r requirements.txt
```

The headline reproduction uses only the Python standard library.

## Reproduce the headline result

```bash
python code/reproduce_headline.py
```

This reads the compact lossless 588×10 binary matrix in `results/mmlu/headline_matrix.json` and verifies the supplied winner certificates in `results/mmlu/headline_certificate.json`.

The reproduced finite-archive result is:

- baseline: Gemini-3.8-Flash, 532/588;
- GPT-6.1-Sol: minimum 3 shared copies for a unique win;
- Claude-Sonnet-5.5: minimum 8 shared copies for a unique win;
- seven other configurations: excluded by blocking-rival certificates.

## Exact regression checks

```bash
python code/test_mmlu_exact.py
python code/test_joint_winners.py
python code/verify_results.py
```

The stored reproduction summary is in `verification/reproduction_checks.json`. It records:

- 1,092 signed vectors and 7,107 subset/budget cases for the exact pairwise implementation;
- 680 joint-winner problems compared with independent brute force;
- a 51-check quantitative consistency audit against the derived result files.

## Reproduce MMLU-ProX-Lite from the pinned public release

```bash
python code/mmlu_release.py \
  --data-root ./data/mmlu_prox \
  --out-dir ./fresh_mmlu \
  --download

python code/joint_winners.py \
  ./fresh_mmlu/aligned_binary_matrix.json \
  --out ./fresh_mmlu/joint_winners.json
```

The loader pins revision `691773a72b353486961d40e99a6c5cbe31c89c43`, checks all 140 English result files, validates source identity/alignment, and rejects duplicate keys or nonbinary exact-match labels.

## Secondary analyses

The repository also contains the analysis code used for:

- MedQA confidence/Brier copy sensitivity and cross-metric transfer;
- weighted Brier, fixed-bin ECE, and weighted-AUROC mass-preservation checks;
- FActScore matched-prompt and verifier controls;
- natural count-transport and literal-deduplication controls;
- the FaStFact conjunction identity analysis.

Compact values used by the manuscript are collected in `results/secondary_summary.json`.

## Data provenance

`DATA.md` lists the public source repositories/releases, pinned revisions or Git blob IDs, archive hashes, expected local paths, and redistribution boundaries. `source_sha256.json` pins the imported source files used by the secondary analyses.

No model inference is required to reproduce the reported analyses from the released outputs.

## Paper material

- Main manuscript: [CopyCAT Research Manuscript Final.pdf](paper/CopyCAT%20Research%20Manuscript%20Final.pdf)
- Reading deck: [CopyCAT Reading Deck.pdf](paper/CopyCAT%20Reading%20Deck.pdf)
- Technical supplement: [CopyCAT Additional Material.pdf](paper/CopyCAT%20Additional%20Material.pdf)
- Supplement source: [CopyCAT_Additional_Material.tex](paper/CopyCAT_Additional_Material.tex)

## Scope

The repository supports finite released-configuration results under the declared one-extra-copy-per-root intervention. It does not estimate the natural prevalence of semantic duplication, infer canonical semantic roots, or establish population-level model superiority.

## Citation

Citation metadata is available in `CITATION.cff`.
