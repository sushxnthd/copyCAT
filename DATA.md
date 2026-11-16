# Public data and exact input identity

## Final MMLU-ProX-Lite extension

Source outputs: https://huggingface.co/datasets/3ae3ae3ae/mmlu-prox-lite-evals

Pinned revision: `691773a72b353486961d40e99a6c5cbe31c89c43`.

`python code/mmlu_release.py --data-root ./data/mmlu_prox --out-dir ./mmlu_fresh --download` enumerates all ten model directories explicitly, reads all fourteen English-domain files per model, checks sizes and Git blob IDs, and writes SHA-256 hashes. The delivered `results/mmlu/source_manifest.json` contains all 140 exact source paths, hashes and byte counts. It is compared on full reproduction; a mismatch fails closed.

There are **588** English questions in these files, not the earlier draft's 583 and not a claim to cover the canonical benchmark's entire split. Every model supplies all 588 roots, so the all-system alignment discards no rows. The raw English score count is 5,880. Domains range from 19 to 68 questions. Alignment uses domain plus `(doc.question_id, doc_hash)` and asserts identical full source documents across shared keys. The loader rejects duplicate keys and nonbinary exact-match labels.

The source card labels its release MIT, describes heterogeneous serving/reasoning settings and single sampled runs, and explicitly says the runs are not intended as a cross-model capability leaderboard. Our equal-question comparisons are finite configuration sensitivity diagnostics. We redistribute a derived binary exact-match matrix and source identifiers, not question texts or generated answers. All original source terms continue to apply.

The final package acquisition command is `python code/run_submission.py --data-root ./data --out-dir ./fresh_reproduction --download`. The first four source groups below are the imported earlier campaign inputs, unchanged and hash-verified.

All analyses reuse public releases; no model inference is needed. This archive does not redistribute the source datasets. Follow the source licenses and terms. `source_sha256.json` pins every one of the 19 input files; the reproduction runner fails closed on missing or changed bytes.

Create this directory layout under your chosen data root:

```
data/
  qwen.csv
  llama.csv
  mistral.csv
  fastfact.jsonl
  factscore/factscore-unlabeled-predictions/  (all 12 JSONL files)
  factscore_human/data/labeled/             (3 JSONL files)
```

## FActScore prediction release

Official repository and release-verification recipe: https://github.com/shmsw25/FActScore

Prediction archive: https://drive.google.com/uc?export=download&id=1lgPqysx2H7zMcyBmuNDztNTAlvfYK0jQ

Archive SHA-256: `449dcd2b34dd9cc4e920ede9be042c8314b3bdce918f416ed42a8b120a28cf5c`.
Extract `factscore-unlabeled-predictions/` inside `data/factscore/`. Keep the original case-sensitive filenames. The archive contains 500 responses per model, with verification labels available only for subsets. The primary full/matched analysis uses ChatGPT_Labels. The fixed two-verifier robustness check uses both ChatGPT_Labels and LLAMA+NP_Labels on exactly the same ChatGPT-label-eligible common prompts.

The score is the response-macro supported-fact fraction following the release-verification recipe. It is unpenalized precision; the optional/default-in-other-workflows gamma length penalty and abstention scores are not evaluated. Do not interpret these numbers as a complete reproduction of every production FActScore configuration.

## FActScore human-annotation release

Human-label archive: https://drive.google.com/uc?export=download&id=155exEdKs7R21gZF4G-x54-XN3qswBcPo

Archive SHA-256: `404482c9a7d588d581a2f7a78d609fe6bfec4ddc0f729c8560a61b1743dbffab`.
Extract beneath `data/factscore_human/` so that `data/labeled/ChatGPT.jsonl`, `InstructGPT.jsonl` and `PerplexityAI.jsonl` appear there.

The exploratory natural-count audit uses sentence annotations with model-atomic-facts and human-atomic-facts. Sentence support is the fraction labeled S among S/NS human facts. Primary human counts include all listed human facts; the S/NS-only alternative is reported separately. Exclude sentences with no S/NS facts or no model facts. Aggregation is within response, then response-macro; bootstrap clusters are biography topics. Per-file hashes and exclusions also appear in `results/natural_summary.json`.

## MedQA confidence release

Repository: https://github.com/JhishanDeb/medqa-confidence

Copy these exact released files to the named local CSVs. The Git blob IDs identify content; retrieve a matching repository revision or use GitHub's public blob API at `https://api.github.com/repos/JhishanDeb/medqa-confidence/git/blobs/BLOB_SHA` and base64-decode its content. Verify the output against `source_sha256.json`.

| Local filename | Repository path | Git blob SHA |
|---|---|---|
| qwen.csv | results/qwen2_5_7b_instruct/per_question.csv | ac0abac9634f16200d8860db81f74b6e5d6271e6 |
| llama.csv | results/llama_3_1_8b_instruct/per_question.csv | 270e0e019920e4d9b8e6622ea0685e40323d3285 |
| mistral.csv | results/mistral_7b_instruct_v0_3/per_question.csv | 2afd9626b5786a9bb6b451bf2c53f0e49ffe6183 |

Each file has 1,273 questions in each of two settings. The analysis asserts aligned question IDs and gold labels. Confidence metrics follow the source `src/medqa_conf/metrics.py`: squared error, 15-bin equal-width ECE and tie-aware Mann–Whitney AUROC. These are secondary analyses of the released outputs, not reruns of source-model inference or validation of medical advice.

## FaStFact scoring-rule control

Repository: https://github.com/Yingjia-Wan/FastFact

Target: `FaStfact-Bench/fastfact-bench_annotated.jsonl`, saved as `data/fastfact.jsonl`.
Git blob SHA: `dfc3e47aa40dbd31350dc2fa88d595808001ed95`.
GitHub blob API: https://api.github.com/repos/Yingjia-Wan/FastFact/git/blobs/dfc3e47aa40dbd31350dc2fa88d595808001ed95

Original protocol: `submission/FaStfact_prospective_prereg_2026-11-13.md`.
Protocol SHA-256: `47ac7d71051fde119313313414570fa2145edb74d94ab51085a25be4b47ad5f0`.

The preserved analysis excludes annotations with action `removed` and invalid/N/A labels, maps exact supported to 1 and other retained final labels to 0, preserves released order, and scores adjacent-pair conjunctions. The current identity audit explains the resulting −9.06-point shift algebraically. It is not treated as independent natural-attack evidence.

Two duplicated prompt blocks create eight repeated model-response records. `audit_fastfact_integrity.py` checks identical outputs/annotations, removes those repeats and resamples prompt clusters. This later robustness analysis remains explicitly post-hoc.

## Integrity and environment

`source_sha256.json` contains all extracted input hashes. `results/source_integrity.json` retains the original archive hashes, byte counts and execution environment. The completed full reproduction reports the current Python version and matches 15 derived output files against the saved results. Use the pinned numerical dependencies in `requirements.txt` when exact seeded bootstrap agreement matters.
