"""Reproduce the compact CopyCAT MMLU headline certificate using only the standard library."""
from pathlib import Path
import base64
import json

ROOT = Path(__file__).resolve().parent.parent
obj = json.loads((ROOT / "results/mmlu/headline_matrix.json").read_text())
cert = json.loads((ROOT / "results/mmlu/headline_certificate.json").read_text())

models = obj["models"]
n = obj["n"]

def unpack_row(encoded):
    raw = base64.b64decode(encoded)
    bits = []
    for byte in raw:
        bits.extend((byte >> shift) & 1 for shift in range(7, -1, -1))
    return bits[:n]

matrix = [unpack_row(row) for row in obj["rows_b64"]]
totals = [sum(row) for row in matrix]

assert totals == obj["baseline_correct_counts"]
baseline = max(range(len(models)), key=lambda i: totals[i])
assert models[baseline] == cert["baseline_winner"] == "gemini-3.8-flash"

attainable = []
for witness in cert["attainable"]:
    target = models.index(witness["model"])
    selected = witness["selected_root_indices"]
    after = [
        totals[j] + sum(matrix[j][i] for i in selected)
        for j in range(len(models))
    ]
    assert after == witness["after_correct_counts"]
    assert all(after[target] > after[j] for j in range(len(models)) if j != target)

    if target != baseline:
        lower_bound = totals[baseline] - totals[target] + 1
        assert len(selected) == lower_bound == witness["minimum_copies"]

    attainable.append((witness["model"], witness["minimum_copies"]))

excluded = []
for certificate in cert["exclusions"]:
    target = models.index(certificate["model"])
    rival = models.index(certificate["blocking_rival"])
    max_advantage = totals[target] - totals[rival] + sum(
        x > y for x, y in zip(matrix[target], matrix[rival])
    )
    assert max_advantage == certificate["maximum_possible_correct_count_advantage"] <= 0
    excluded.append(certificate["model"])

assert set(attainable) == {
    ("gemini-3.8-flash", 0),
    ("gpt-6.1-sol", 3),
    ("claude-sonnet-5-5", 8),
}
assert len(excluded) == 7

print(json.dumps({
    "status": "PASS",
    "n_roots": n,
    "n_configurations": len(models),
    "baseline_winner": models[baseline],
    "baseline_correct_counts": dict(zip(models, totals)),
    "attainable_unique_winners_and_minimum_copies": dict(attainable),
    "exactly_excluded_models": excluded,
}, indent=2))
