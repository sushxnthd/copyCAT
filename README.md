# CopyCAT

**Copy-Controlled Attainability Testing**  
Companion reproducibility repository for **“CopyCAT: Exact Winner Certificates When One Fact Counts Twice.”**

CopyCAT asks a narrow decision question: with every released prediction and label frozen, if selected existing evaluation roots may be counted twice under **one common schedule across systems**, which leaderboard outcomes are attainable, how many copies are required, and which winners are impossible?

## 60-second judge check

No API key, model inference, GPU, network access, or package installation is required:

```bash
python code/quick_demo.py
python code/verify_repo_claims.py
```

The demo independently recomputes the headline from a compact lossless encoding of the delivered 588×10 binary score matrix:

- baseline winner: **Gemini-3.8-Flash, 532/588**
- **GPT-6.1-Sol** becomes uniquely first after **3 shared copies**; 3 is necessary and sufficient
- **Claude-Sonnet-5.5** becomes uniquely first after **8 shared copies**; 8 is necessary and sufficient
- the remaining **7 configurations are exactly excluded** from becoming unique winners under the one-extra-copy-per-root contract
- possible unique winners: **{Gemini, GPT, Claude}**

The witness root indices and blocking-rival exclusion certificates are in [`results/mmlu/headline_certificate.json`](results/mmlu/headline_certificate.json).

## Independent verification

With NumPy/SciPy installed:

```bash
python code/test_mmlu_exact.py
python code/test_joint_winners.py
```

The recovered submission artifact was rerun before this repository was populated:

- MMLU exact enumeration: **PASS — 1,092 signed vectors / 7,107 subset-budget cases**
- joint-winner verification: **PASS — 680 brute-force cases**
- manuscript quantitative audit: **PASS — 51 checks**
- headline demo: **PASS**

See [`verification/JUDGE_CHECKS.json`](verification/JUDGE_CHECKS.json).

## What CopyCAT certifies

For the declared threat family:

1. predictions and labels are fixed;
2. roots are existing aligned evaluation units;
3. each root may receive at most one extra copy;
4. the same copied-root schedule is applied to every system;
5. pairwise extrema are attained exactly;
6. minimum-copy counterexamples are reported;
7. joint unique-winner feasibility uses one common schedule;
8. impossible winners receive exact certificates.

The broad phenomenon that multiplicity/reweighting can change rankings is prior work. CopyCAT does **not** claim a first-ever sensitivity framework. The closest-work boundary is documented in [`docs/CLOSE_PRIOR_ART_AUDIT.md`](docs/CLOSE_PRIOR_ART_AUDIT.md), and the shared-schedule computational distinction is documented in [`docs/JOINT_WINNER_PROOF.md`](docs/JOINT_WINNER_PROOF.md).

## Headline empirical results

### MMLU-ProX-Lite

Pinned English archive: **588 aligned questions × 10 released configurations**.

At the 10% budget, `B=58`:

- **24 / 45** pooled strict orders can reverse
- **1 / 45** is tie-only
- **20 / 45** remain strictly robust

Compact result files:

- [`results/mmlu/headline_matrix.json`](results/mmlu/headline_matrix.json) — lossless bit-packed score matrix
- [`results/mmlu/headline_certificate.json`](results/mmlu/headline_certificate.json) — minimum witnesses and exact exclusions
- [`results/mmlu/pooled_summary.json`](results/mmlu/pooled_summary.json) — pooled decision classes

### Secondary analyses

[`results/secondary_summary.json`](results/secondary_summary.json) records the compact secondary checks:

- MedQA: 18 Brier comparisons; 4 reversible within `B=127`, 14 robust; minimum reversal budgets 71, 77, 100, 105
- mass-preserving repair: 132 Brier / fixed-bin ECE / weighted-AUROC checks restored within `1e-12`
- FActScore: selected 79-prompt Alpaca-7B/Vicuna-13B existence witness reverses under both released verifiers
- natural-count transport: aggregate shift but no matched-topic model-order reversal

These are deliberately scoped results, not evidence that natural semantic duplication is common.

## Reproduce the pinned MMLU audit from the public source

Install:

```bash
python -m pip install -r requirements.txt
```

Acquire and audit the exact pinned English source release:

```bash
python code/mmlu_release.py \
  --data-root ./data/mmlu_prox \
  --out-dir ./fresh_mmlu \
  --download

python code/joint_winners.py \
  ./fresh_mmlu/aligned_binary_matrix.json \
  --out ./fresh_mmlu/joint_winners.json
```

`mmlu_release.py` verifies the pinned dataset revision, all 140 English result files, source sizes/hashes, binary labels, duplicate keys, and cross-system question identity before producing the aligned matrix.

For the imported FActScore, MedQA, and FaStFact public releases, exact sources, revisions, hashes, and licensing boundaries are in [`DATA.md`](DATA.md). `code/acquire_sources.py` downloads and hash-verifies those inputs.

## Repository map

```text
code/           certificate algorithms, analyses, tests, and acquisition tools
results/        compact judge-facing result/certificate files
verification/   fresh PASS record from the recovered submitted artifact
docs/           prior-art audit and joint-winner proof note
examples/       minimal generic CopyCAT audit input
DATA.md         public inputs, pinned revisions, hashes, and redistribution boundaries
CODE_PROVENANCE.md  pre-sprint vs imported vs final-revision provenance
```

## Provenance and scope

[`CODE_PROVENANCE.md`](CODE_PROVENANCE.md) distinguishes pre-sprint GRIT ideas, imported earlier campaign modules, and code written in the final sprint revision.

This repository establishes **finite released-configuration results under a declared synthetic copy intervention**. It does not establish natural attack prevalence, semantic-root discovery, population-level model superiority, unseen factuality confirmation, or security under arbitrary deletions/repetitions/weight changes.

No result here was newly invented for GitHub; this repository exposes and rechecks the code and evidence underlying the submitted project.
