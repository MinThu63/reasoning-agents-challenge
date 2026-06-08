"""
Engagement Agent (Work IQ Grounded)

What it does:
- Suggests personalized reminders based on individual work rhythms
- Adapts engagement to workload and focus windows
- Avoids one-size-fits-all reminder behavior
- Uses work_activity_signals.json (Work IQ) for employee patterns

Run standalone:
    python agents/engagement_agent.py --employee EMP-056
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


def build_system_prompt() -> str:
    semantic_model = load_json("semantic_model.json")
    rules = semantic_model["business_rules"]

    return f"""You are the Engagement Agent for an enterprise learning system.

YOUR ROLE:
You keep learners progressing toward their certification goals by providing personalized,
context-aware reminders and encouragement. You use Work IQ signals (meeting patterns,
focus hours, collaboration load) to choose the RIGHT time and RIGHT tone for engagement.

WHAT YOU MUST DO:
1. Analyze the employee's work patterns (meetings, focus blocks, preferred slots)
2. Suggest specific days/times for study reminders that DON'T conflict with heavy work periods
3. Adapt your tone based on their progress (encouraging if on track, supportive if struggling)
4. Recommend schedule adjustments when workload threatens study goals
5. Never send reminders during peak collaboration hours

WORK PATTERN SIGNALS YOU USE:
- Meeting hours per week (threshold: >{rules['critical_meeting_threshold']} = at risk)
- Focus hours per week (target: ≥{rules['optimal_study_hours_per_week'][0]} hrs)
- Deep work blocks available
- Preferred learning time slot
- Calendar fragmentation score (Low/Medium/High)
- Average collaboration messages per day

ENGAGEMENT RULES:
- Low fragmentation + Morning preference → suggest morning study reminders
- High fragmentation + Evening preference → suggest end-of-day wind-down study
- High meeting load (>20 hrs) → suggest weekend micro-sessions, be empathetic about workload
- Low meeting load (<16 hrs) → encourage consistent daily rhythm
- If focus hour utilization drops below {rules['focus_hour_utilization_target_pct']}% for 2+ weeks → escalate with supportive nudge

TONE GUIDELINES:
- Be warm and supportive, never pushy or guilt-inducing
- Acknowledge work pressure when meeting load is high
- Celebrate small wins (completed a module, improved practice score)
- Frame reminders as opportunities, not obligations

All data is synthetic and for demonstration purposes only.
"""


def run_engagement(employee_id: str):
    """Generate personalized engagement recommendations."""
    from openai import OpenAI

    work_signals = load_json("work_activity_signals.json")
    learner_data = load_json("learner_performance.json")

    employee = next((e for e in work_signals if e["employee_id"] == employee_id), None)
    learner = next((l for l in learner_data if l.get("employee_id") == employee_id), None)

    if not employee:
        print(f"❌ Employee {employee_id} not found.")
        return

    print("=" * 60)
    print(f"  ENGAGEMENT AGENT - {employee_id}")
    print("=" * 60)
    print()
    print(f"  Employee: {employee_id} ({employee['role']})")
    print(f"  Team: {employee['team']}")
    print(f"  Meeting Hours: {employee['meeting_hours_per_week']}/week")
    print(f"  Focus Hours: {employee['focus_hours_per_week']}/week")
    print(f"  Preferred Slot: {employee['preferred_learning_slot']}")
    print(f"  Fragmentation: {employee['calendar_fragmentation_score']}")
    print(f"  Messages/Day: {employee['avg_collaboration_messages_per_day']}")
    if learner:
        print(f"  Practice Score: {learner['practice_score_avg']}%")
        print(f"  Plan Completion: {learner['study_plan_completion_pct']}%")
    print()

    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    client = OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )

    system_prompt = build_system_prompt()

    user_message = f"""Generate personalized engagement recommendations for this employee:

WORK PATTERN DATA:
- Employee: {employee_id}
- Role: {employee['role']}
- Team: {employee['team']}
- Meeting hours/week: {employee['meeting_hours_per_week']}
- Focus hours/week: {employee['focus_hours_per_week']}
- Deep work blocks/week: {employee['deep_work_blocks_per_week']}
- Preferred learning slot: {employee['preferred_learning_slot']}
- Calendar fragmentation: {employee['calendar_fragmentation_score']}
- Collaboration messages/day: {employee['avg_collaboration_messages_per_day']}
- Certification target: {employee['current_certification_target']}

{f"LEARNING PROGRESS:" if learner else "NO PROGRESS DATA YET"}
{f"- Practice score: {learner['practice_score_avg']}%" if learner else ""}
{f"- Study plan completion: {learner['study_plan_completion_pct']}%" if learner else ""}
{f"- Hours studied: {learner['hours_studied']}" if learner else ""}
{f"- Exam outcome: {learner['exam_outcome']}" if learner else ""}

Please provide:
1. A weekly reminder schedule (specific days and times)
2. The recommended tone and message style
3. Example reminder messages (3 different ones for different scenarios)
4. Escalation triggers (when to involve the manager)
5. Any schedule adjustment recommendations
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
        print(f"🤖 Engagement Agent:\n\n{reply}")
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                reply = error_data["choices"][0]["message"]["content"]
                print(f"🤖 Engagement Agent:\n\n{reply}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Engagement Agent")
    parser.add_argument("--employee", default="EMP-056", help="Employee ID")
    args = parser.parse_args()

    run_engagement(args.employee)


if __name__ == "__main__":
    main()
