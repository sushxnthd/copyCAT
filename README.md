# CopyCAT

**Copy-Controlled Attainability Testing** for fixed evaluation archives.

This repository is the judge-facing reproducibility package for **“CopyCAT: Exact Winner Certificates When One Fact Counts Twice”**, prepared for the Apart AI × Epistemics Research Sprint (16 November 2026).

## What CopyCAT audits

CopyCAT freezes released predictions and labels, declares stable evaluation roots, and asks what happens if up to a bounded number of existing roots receive one extra copy under **one common copied-root schedule across all systems**.

For the pinned 588-question English MMLU-ProX-Lite archive used in the paper:

- three shared copies make the runner-up uniquely first;
- eight shared copies make the third configuration uniquely first;
- seven configurations are exactly excluded from ever becoming unique winners under the allowed intervention;
- at a 10% budget, 24/45 pooled strict orders can reverse, 1 can tie only, and 20 remain strictly ordered.

These are finite released-configuration sensitivity results under a declared synthetic copy intervention. They are not population capability rankings and do not estimate how often natural semantic duplication occurs.

## Quick demo

Python 3.12+ is recommended. The headline demo uses only the Python standard library and the supplied derived binary matrix:

```bash
python code/quick_demo.py
```

It recomputes the three-copy and eight-copy winners, checks every rival, proves the minimum copy counts, and emits all seven integer exclusions.

## Full reproduction

Install the pinned numerical dependencies:

```bash
python -m pip install -r requirements.txt
```

Acquire the public source bytes and rerun the full analysis into a fresh directory:

```bash
python code/run_submission.py --data-root ./data --out-dir ./fresh_reproduction --download
```

The runner fails closed on changed source bytes, failed scripts, unmatched reference results, or unverified solver statuses. No model inference, GPU, paid API, or API key is required.

## Repository map

- `code/` — CopyCAT audit, exact tests, joint-winner solver checks, secondary analyses, and reproduction runners.
- `results/mmlu/` — aligned binary matrix, exact pairwise results, witnesses, joint-winner certificates, and source manifest.
- `results/` — MedQA, factuality, natural-count, and mass-preserving-repair outputs used in the report.
- `DATA.md` — exact public sources, pinned revisions/blob IDs, hashes, and local layout.
- `CODE_PROVENANCE.md` — pre-sprint, imported campaign, and final-revision code boundary.
- `submission/JOINT_WINNER_PROOF.md` — solver-independent integer argument for the headline possible-winner set.
- `submission/DEMO_SCRIPT.md` — short judge demonstration outline.

## Scientific boundary

Ordinary reweighting sensitivity, mass conservation, weighted metrics, and election-control ideas are established prior work. CopyCAT’s contribution is the bounded shared-copy audit, its joint-winner attainability/exclusion certificates, and the finite empirical audit under that contract. Pairwise reversibility is not treated as proof that a target can beat every rival under one schedule.

The current manuscript source is maintained in the project Google Doc; the code and derived evidence in this repository are the reproducibility surface for submission.
