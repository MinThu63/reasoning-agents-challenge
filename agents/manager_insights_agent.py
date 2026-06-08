"""
Manager Insights Agent (Work IQ + Fabric IQ Grounded)

What it does:
- Summarizes learning progress by team, role, or certification track
- Highlights capacity-constrained teams or exam risk areas
- Presents insights without exposing sensitive personal data
- Uses learner_performance.json + work_activity_signals.json + semantic_model.json

Run standalone:
    python agents/manager_insights_agent.py --team TEAM-B
    python agents/manager_insights_agent.py --all
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-oss-120b")
API_KEY = os.getenv("AZURE_AI_API_KEY", "")

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def get_team_summary(team_id: str = None) -> dict:
    """Aggregate team metrics without exposing individual data."""
    learner_data = load_json("learner_performance.json")
    work_signals = load_json("work_activity_signals.json")
    semantic_model = load_json("semantic_model.json")

    # Filter by team if specified
    if team_id:
        learners = [l for l in learner_data if l.get("team") == team_id]
        workers = [w for w in work_signals if w.get("team") == team_id]
    else:
        learners = learner_data
        workers = work_signals

    if not learners:
        return {"error": f"No data for team {team_id}"}

    # Aggregate metrics
    total = len(learners)
    passed = sum(1 for l in learners if l["exam_outcome"] == "Pass")
    failed = sum(1 for l in learners if l["exam_outcome"] == "Fail")
    avg_score = sum(l["practice_score_avg"] for l in learners) / total
    avg_hours = sum(l["hours_studied"] for l in learners) / total
    avg_completion = sum(l["study_plan_completion_pct"] for l in learners) / total

    # Work signals
    avg_meetings = sum(w["meeting_hours_per_week"] for w in workers) / len(workers) if workers else 0
    avg_focus = sum(w["focus_hours_per_week"] for w in workers) / len(workers) if workers else 0
    at_risk = sum(1 for w in workers if w["meeting_hours_per_week"] > 20)

    # Team info from semantic model
    team_info = next((t for t in semantic_model["teams"] if t["team_id"] == team_id), None) if team_id else None

    return {
        "team_id": team_id or "ALL",
        "team_name": team_info["name"] if team_info else "All Teams",
        "total_learners": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(passed / total * 100, 1),
        "avg_practice_score": round(avg_score, 1),
        "avg_hours_studied": round(avg_hours, 1),
        "avg_study_plan_completion_pct": round(avg_completion, 1),
        "avg_meeting_hours": round(avg_meetings, 1),
        "avg_focus_hours": round(avg_focus, 1),
        "employees_at_risk": at_risk,
        "at_risk_pct": round(at_risk / len(workers) * 100, 1) if workers else 0,
    }


def build_system_prompt() -> str:
    semantic_model = load_json("semantic_model.json")
    rules = semantic_model["business_rules"]

    return f"""You are the Manager Insights Agent for an enterprise learning system.

YOUR ROLE:
You provide team-level visibility into certification readiness and workforce development.
You present aggregate insights to managers without exposing sensitive individual data.

WHAT YOU MUST DO:
1. Summarize learning progress by team, role, or certification track
2. Highlight patterns (capacity-constrained teams, exam risk areas)
3. Compare team performance against business rules and benchmarks
4. Recommend actions managers can take to improve team outcomes
5. NEVER expose individual employee names, scores, or personal data

BUSINESS RULES & BENCHMARKS:
- Optimal meeting hours: {rules['optimal_meeting_hours_range'][0]}-{rules['optimal_meeting_hours_range'][1]} hrs/week
- Critical threshold: >{rules['critical_meeting_threshold']} hrs/week = at risk
- Target practice score: ≥{rules['minimum_practice_score_for_exam_approval']}%
- Focus hour target: {rules['focus_hour_utilization_target_pct']}%
- Study hours target: {rules['optimal_study_hours_per_week'][0]}-{rules['optimal_study_hours_per_week'][1]} hrs/week

TEAM BENCHMARKS:
{json.dumps(semantic_model["teams"], indent=2)}

PRESENTATION RULES:
- Use aggregate numbers only (averages, percentages, counts)
- Frame risks as team-level patterns, not individual failures
- Always include actionable recommendations
- Compare against benchmarks to show where teams stand
- Use tables for clarity

All data is synthetic and for demonstration purposes only.
"""


def run_insights(team_id: str = None):
    """Generate manager insights for a team or all teams."""
    from openai import OpenAI

    # Get aggregated data
    if team_id:
        summary = get_team_summary(team_id)
    else:
        # Get all teams
        summaries = []
        for tid in ["TEAM-A", "TEAM-B", "TEAM-C", "TEAM-D", "TEAM-E"]:
            s = get_team_summary(tid)
            if "error" not in s:
                summaries.append(s)
        summary = {"all_teams": summaries, "overall": get_team_summary()}

    print("=" * 60)
    print(f"  MANAGER INSIGHTS AGENT - {team_id or 'All Teams'}")
    print("=" * 60)
    print()

    if team_id and "error" not in summary:
        print(f"  Team: {summary['team_name']} ({team_id})")
        print(f"  Learners: {summary['total_learners']}")
        print(f"  Pass Rate: {summary['pass_rate_pct']}%")
        print(f"  Avg Practice Score: {summary['avg_practice_score']}%")
        print(f"  At-Risk Employees: {summary['employees_at_risk']} ({summary['at_risk_pct']}%)")
        print()

    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    client = OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )

    system_prompt = build_system_prompt()

    user_message = f"""Generate a manager insights report based on this aggregated team data:

{json.dumps(summary, indent=2)}

Provide:
1. Executive summary (3-4 sentences)
2. Key metrics table
3. Risk areas and patterns
4. Comparison against benchmarks
5. Recommended actions (specific, actionable)
6. Team health rating (Green / Yellow / Red)
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=messages,
        )
        reply = response.choices[0].message.content
        print(f"🤖 Manager Insights:\n\n{reply}")
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                reply = error_data["choices"][0]["message"]["content"]
                print(f"🤖 Manager Insights:\n\n{reply}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manager Insights Agent")
    parser.add_argument("--team", default=None, help="Team ID (e.g., TEAM-B) or omit for all teams")
    parser.add_argument("--all", action="store_true", help="Show all teams")
    args = parser.parse_args()

    run_insights(args.team)


if __name__ == "__main__":
    main()
