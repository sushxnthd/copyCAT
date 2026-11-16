"""Check the compact derived results and stored reproduction record for consistency."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
load = lambda p: json.loads((ROOT / p).read_text())

matrix = load("results/mmlu/headline_matrix.json")
certificate = load("results/mmlu/headline_certificate.json")
pooled = load("results/mmlu/pooled_summary.json")
secondary = load("results/secondary_summary.json")
record = load("verification/reproduction_checks.json")

assert matrix["n"] == 588 and matrix["shape"] == [10, 588]
assert len(matrix["models"]) == 10
assert certificate["baseline_winner"] == "gemini-3.8-flash"

minimums = {x["model"]: x["minimum_copies"] for x in certificate["attainable"]}
assert minimums == {
    "claude-sonnet-5-5": 8,
    "gemini-3.8-flash": 0,
    "gpt-6.1-sol": 3,
}
assert len(certificate["exclusions"]) == 7
assert pooled == {
    "B": 58,
    "strict_pairs": 45,
    "reversible": 24,
    "tie_only": 1,
    "strictly_robust": 20,
}
assert secondary["medqa"]["comparisons"] == 18
assert secondary["medqa"]["reversible"] == 4
assert secondary["medqa"]["robust"] == 14
assert secondary["medqa"]["minimum_reversal_budgets"] == [71, 77, 100, 105]
assert secondary["mass_preserving_repair"]["checks"] == 132
assert secondary["mass_preserving_repair"]["max_abs_error"] <= 1e-12
assert secondary["factscore"]["n"] == 79
assert secondary["factscore"]["two_verifiers_reverse"] is True
assert secondary["natural_counts"]["matched_order_reversals"] == 0

assert record["status"] == "PASS"
assert record["checks"]["mmlu_exact"]["signed_vectors"] == 1092
assert record["checks"]["mmlu_exact"]["subset_budget_cases"] == 7107
assert record["checks"]["joint_bruteforce"]["cases"] == 680
assert record["checks"]["quantitative_consistency"]["checks"] == 51

print(json.dumps({
    "status": "PASS",
    "headline": {
        "roots": 588,
        "configurations": 10,
        "possible_winners": [
            "gemini-3.8-flash",
            "gpt-6.1-sol",
            "claude-sonnet-5-5",
        ],
        "minimum_copies": minimums,
        "exact_exclusions": 7,
        "pooled_B58": pooled,
    },
    "secondary": secondary,
    "regression_record": record["checks"],
}, indent=2))
