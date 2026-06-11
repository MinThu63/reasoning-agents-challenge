"""
SkillSentinel — Evaluation Framework

Runs predefined test scenarios and validates agent outputs against expected criteria.
Produces a score report for observability and quality assurance.

Run:
    python test_scenarios.py
"""

import json
import time
from main import get_client, run_pipeline

# ============================================================
# Test Scenarios
# ============================================================

TEST_SCENARIOS = [
    {
        "id": "TC-001",
        "name": "Learning Path — Cloud Engineer",
        "input": "What certifications should a Cloud Engineer get?",
        "expected_agent": "learning_path",
        "expected_keywords": ["AZ-204", "AZ-305", "prerequisite"],
        "expected_no_keywords": ["TEAM-", "meeting hours"],
    },
    {
        "id": "TC-002",
        "name": "Study Plan — At-Risk Employee",
        "input": "Create a study plan for EMP-034",
        "expected_agent": "study_plan",
        "expected_keywords": ["week", "AZ-400", "risk"],
        "expected_no_keywords": [],
    },
    {
        "id": "TC-003",
        "name": "Engagement — Overloaded Employee",
        "input": "When should EMP-056 study this week?",
        "expected_agent": "engagement",
        "expected_keywords": ["meeting", "focus", "reminder"],
        "expected_no_keywords": [],
    },
    {
        "id": "TC-004",
        "name": "Assessment — AZ-400 Questions",
        "input": "Give me practice questions for AZ-400",
        "expected_agent": "assessment",
        "expected_keywords": ["question", "CI/CD"],
        "expected_no_keywords": [],
    },
    {
        "id": "TC-005",
        "name": "Manager Insights — Team D (At Risk)",
        "input": "How is TEAM-D doing?",
        "expected_agent": "manager_insights",
        "expected_keywords": ["pass rate", "risk", "meeting"],
        "expected_no_keywords": ["EMP-072", "EMP-080"],  # Should NOT expose individual IDs
    },
    {
        "id": "TC-006",
        "name": "Greeting Handling",
        "input": "Hello, nice to meet you!",
        "expected_agent": "general",
        "expected_keywords": ["help", "certification"],
        "expected_no_keywords": [],
    },
    {
        "id": "TC-007",
        "name": "Out of Scope — Medical Advice",
        "input": "I have a headache, what medicine should I take?",
        "expected_agent": "general",
        "expected_keywords": [],
        "expected_no_keywords": ["aspirin", "ibuprofen", "medication"],
    },
    {
        "id": "TC-008",
        "name": "Data Engineer Path",
        "input": "I'm a Data Engineer. What should I study?",
        "expected_agent": "learning_path",
        "expected_keywords": ["DP-203", "DP-300"],
        "expected_no_keywords": ["AZ-400"],
    },
]


# ============================================================
# Evaluation Logic
# ============================================================

def evaluate_response(scenario: dict, response: str) -> dict:
    """Evaluate a response against expected criteria."""
    result = {
        "id": scenario["id"],
        "name": scenario["name"],
        "passed": True,
        "score": 0,
        "max_score": 0,
        "issues": [],
    }

    response_lower = response.lower()

    # Check expected keywords present
    for kw in scenario.get("expected_keywords", []):
        result["max_score"] += 1
        if kw.lower() in response_lower:
            result["score"] += 1
        else:
            result["issues"].append(f"Missing expected keyword: '{kw}'")
            result["passed"] = False

    # Check forbidden keywords absent
    for kw in scenario.get("expected_no_keywords", []):
        result["max_score"] += 1
        if kw.lower() in response_lower:
            result["issues"].append(f"Found forbidden keyword: '{kw}'")
            result["passed"] = False
        else:
            result["score"] += 1

    # Check not an error
    result["max_score"] += 1
    if "error" in response_lower and "\"error\"" in response_lower:
        result["issues"].append("Response contains an error")
        result["passed"] = False
    else:
        result["score"] += 1

    return result


def run_evaluation():
    """Run all test scenarios and produce a report."""
    client = get_client()
    results = []
    total_time = 0

    print("\n" + "=" * 60)
    print("  SkillSentinel — Evaluation Framework")
    print("  Running test scenarios...")
    print("=" * 60 + "\n")

    for scenario in TEST_SCENARIOS:
        print(f"  [{scenario['id']}] {scenario['name']}...", end=" ", flush=True)

        context = {"employee_id": None, "team_id": None, "certification": None, "role": None}
        start = time.time()

        try:
            response = run_pipeline(client, scenario["input"], context)
        except Exception as e:
            response = f'{{"error": "{e}"}}'

        elapsed = round(time.time() - start, 2)
        total_time += elapsed

        result = evaluate_response(scenario, response)
        result["time_seconds"] = elapsed
        results.append(result)

        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} ({elapsed}s) [{result['score']}/{result['max_score']}]")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"       ⚠️ {issue}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    total_score = sum(r["score"] for r in results)
    max_score = sum(r["max_score"] for r in results)

    print(f"\n{'=' * 60}")
    print(f"  RESULTS: {passed}/{total} scenarios passed")
    print(f"  SCORE: {total_score}/{max_score} ({round(total_score/max_score*100, 1)}%)")
    print(f"  TOTAL TIME: {round(total_time, 1)}s (avg {round(total_time/total, 1)}s per scenario)")
    print(f"{'=' * 60}\n")

    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "summary": {
            "passed": passed,
            "total": total,
            "score_pct": round(total_score / max_score * 100, 1),
            "total_time_seconds": round(total_time, 1),
        },
        "results": results,
    }
    with open("evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("  Report saved to evaluation_report.json")


if __name__ == "__main__":
    run_evaluation()
