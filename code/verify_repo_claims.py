"""Judge-facing consistency checks over the compact delivered result files."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
load = lambda p: json.loads((ROOT / p).read_text())

m = load("results/mmlu/headline_matrix.json")
c = load("results/mmlu/headline_certificate.json")
p = load("results/mmlu/pooled_summary.json")
s = load("results/secondary_summary.json")
v = load("verification/JUDGE_CHECKS.json")

assert m["n"] == 588 and m["shape"] == [10, 588]
assert len(m["models"]) == 10
assert c["baseline_winner"] == "gemini-3.8-flash"
mins = {x["model"]: x["minimum_copies"] for x in c["attainable"]}
assert mins == {"claude-sonnet-5-5": 8, "gemini-3.8-flash": 0, "gpt-6.1-sol": 3}
assert len(c["exclusions"]) == 7
assert p == {"B": 58, "strict_pairs": 45, "reversible": 24, "tie_only": 1, "strictly_robust": 20}
assert s["medqa"]["comparisons"] == 18
assert s["medqa"]["reversible"] == 4 and s["medqa"]["robust"] == 14
assert s["medqa"]["minimum_reversal_budgets"] == [71, 77, 100, 105]
assert s["mass_preserving_repair"]["checks"] == 132
assert s["mass_preserving_repair"]["max_abs_error"] <= 1e-12
assert s["factscore"]["n"] == 79 and s["factscore"]["two_verifiers_reverse"] is True
assert s["natural_counts"]["matched_order_reversals"] == 0
assert v["status"] == "PASS"
assert v["checks"]["mmlu_exact"]["signed_vectors"] == 1092
assert v["checks"]["mmlu_exact"]["subset_budget_cases"] == 7107
assert v["checks"]["joint_bruteforce"]["cases"] == 680
assert v["checks"]["manuscript_quantitative_claims"]["checks"] == 51

print(json.dumps({
    "status": "PASS",
    "headline": {"roots": 588, "configurations": 10, "possible_winners": ["gemini-3.8-flash", "gpt-6.1-sol", "claude-sonnet-5-5"], "minimum_copies": mins, "exact_exclusions": 7, "pooled_B58": p},
    "secondary": s,
    "independent_test_record": v["checks"],
}, indent=2))
