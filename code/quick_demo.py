"""Standard-library CopyCAT headline reproduction from the compact delivered score matrix."""
from pathlib import Path
import base64, json

ROOT = Path(__file__).resolve().parent.parent
obj = json.loads((ROOT / "results/mmlu/headline_matrix.json").read_text())
cert = json.loads((ROOT / "results/mmlu/headline_certificate.json").read_text())
models = obj["models"]
n = obj["n"]

def unpack_row(s):
    raw = base64.b64decode(s)
    bits = []
    for byte in raw:
        bits.extend((byte >> shift) & 1 for shift in range(7, -1, -1))
    return bits[:n]

a = [unpack_row(s) for s in obj["rows_b64"]]
totals = [sum(row) for row in a]
assert totals == obj["baseline_correct_counts"]
best = max(range(len(models)), key=lambda i: totals[i])
assert models[best] == cert["baseline_winner"] == "gemini-3.8-flash"

attained = []
for w in cert["attainable"]:
    target = models.index(w["model"])
    ids = w["selected_root_indices"]
    after = [totals[j] + sum(a[j][i] for i in ids) for j in range(len(models))]
    assert after == w["after_correct_counts"]
    assert all(after[target] > after[j] for j in range(len(models)) if j != target)
    if target != best:
        lower_bound = totals[best] - totals[target] + 1
        assert len(ids) == lower_bound == w["minimum_copies"]
    attained.append((w["model"], w["minimum_copies"]))

exclusions = []
for x in cert["exclusions"]:
    t = models.index(x["model"])
    b = models.index(x["blocking_rival"])
    maximum_advantage = totals[t] - totals[b] + sum(x1 > y1 for x1, y1 in zip(a[t], a[b]))
    assert maximum_advantage == x["maximum_possible_correct_count_advantage"] <= 0
    exclusions.append(x["model"])

assert set(attained) == {("gemini-3.8-flash", 0), ("gpt-6.1-sol", 3), ("claude-sonnet-5-5", 8)}
assert len(exclusions) == 7

print(json.dumps({
    "status": "PASS",
    "n_roots": n,
    "n_configurations": len(models),
    "baseline_winner": models[best],
    "baseline_correct_counts": dict(zip(models, totals)),
    "attainable_unique_winners_and_minimum_copies": dict(attained),
    "exactly_excluded_models": exclusions,
    "scope": "finite released archive; fixed outputs/labels; one shared schedule; at most one extra copy per root",
}, indent=2))
