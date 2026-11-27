# Reproduce CopyCAT

The headline result is designed to be independently checkable without model inference or a paid API.

## Environment

Python 3.12+ is recommended. The headline certificate check uses only the Python standard library.

## Headline reproduction

```bash
python code/reproduce_headline.py
```

Expected finite-archive result on the committed 588×10 matrix:

- baseline winner: Gemini-3.8-Flash, 532/588;
- GPT-6.1-Sol: minimum 3 shared copies for a unique win;
- Claude-Sonnet-5.5: minimum 8 shared copies for a unique win;
- seven other configurations excluded by blocking-rival certificates.

## Exact regression checks

```bash
python code/test_mmlu_exact.py
python code/test_joint_winners.py
python code/verify_results.py
```

The stored verification summary is `verification/reproduction_checks.json`. It records 1,092 signed vectors and 7,107 subset/budget cases, 680 joint-winner problems checked against independent brute force, and a 51-check consistency audit.

## Public-source reconstruction

See [DATA.md](DATA.md) for pinned source revisions, hashes, redistribution boundaries and the full acquisition command. The headline check above operates only on the committed derived matrix and certificates.

## Scope

This reproduces the finite-archive certificate result for the pinned release. It is not a claim about population-level model superiority or naturally occurring semantic duplication.
