"""
Study Plan Generator Agent (Fabric IQ Grounded)

What it does:
- Recommends milestones at role level
- Allocates study hours accounting for workload and schedule
- Adjusts sequencing based on difficulty and prerequisites
- Uses semantic_model.json (Fabric IQ) for certification data, study templates, and business rules
- Uses work_activity_signals.json for employee workload context

Run standalone:
    python agents/study_plan_generator.py

Test with:
    python agents/study_plan_generator.py --employee EMP-034
"""

import json
import sys
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


def get_employee_context(employee_id: str) -> dict:
    """Look up a specific employee's work signals and learner performance."""
    work_signals = load_json("work_activity_signals.json")
    learner_data = load_json("learner_performance.json")

    employee = next((e for e in work_signals if e["employee_id"] == employee_id), None)
    learner = next((l for l in learner_data if l.get("employee_id") == employee_id), None)

    return {"work_signals": employee, "learner_data": learner}


def get_certification_details(cert_id: str) -> dict:
    """Get certification details from semantic model."""
    semantic_model = load_json("semantic_model.json")
    cert = next((c for c in semantic_model["certifications"] if c["id"] == cert_id), None)
    template = next((t for t in semantic_model["study_plan_templates"] if t["certification_id"] == cert_id), None)
    return {"certification": cert, "study_template": template}


def build_system_prompt() -> str:
    """Build the Study Plan Generator's system prompt with Fabric IQ data."""
    semantic_model = load_json("semantic_model.json")
    rules = semantic_model["business_rules"]

    return f"""You are the Study Plan Generator Agent for an enterprise learning system.

YOUR ROLE:
You create personalized, capacity-aware study plans for employees preparing for Microsoft certifications.
You ground your recommendations in structured business data (Fabric IQ semantic layer).

WHAT YOU MUST DO:
1. Recommend weekly milestones based on the certification's study template
2. Allocate study hours accounting for the employee's current meeting load and focus hours
3. Adjust the timeline if the employee is above the critical meeting threshold
4. Include specific target practice scores for each milestone week
5. Flag risks and suggest schedule adjustments

BUSINESS RULES:
- Optimal meeting hours: {rules['optimal_meeting_hours_range'][0]}-{rules['optimal_meeting_hours_range'][1]} hrs/week
- Recommended study hours: {rules['optimal_study_hours_per_week'][0]}-{rules['optimal_study_hours_per_week'][1]} hrs/week
- Critical meeting threshold: >{rules['critical_meeting_threshold']} hrs/week
- Minimum practice score before exam: {rules['minimum_practice_score_for_exam_approval']}%
- Focus hour utilization target: {rules['focus_hour_utilization_target_pct']}%

AVAILABLE CERTIFICATIONS AND STUDY HOURS:
{json.dumps([{"id": c["id"], "name": c["name"], "hours": c["recommended_study_hours"], "difficulty": c["difficulty_level"], "prerequisites": c["prerequisites"]} for c in semantic_model["certifications"]], indent=2)}

STUDY PLAN TEMPLATES:
{json.dumps(semantic_model["study_plan_templates"], indent=2)}

RESPONSE FORMAT:
- Always provide a week-by-week plan with specific topics and target scores
- Include total estimated duration
- Flag if the employee's workload puts them at risk
- Suggest the best study time slots based on their preferred learning slot
- Recommend when to take practice exams and when to schedule the real exam

All data is synthetic and for demonstration purposes only.
"""


def run_study_plan(employee_id: str, certification: str = None):
    """Generate a study plan for a specific employee."""
    from openai import OpenAI

    # Get employee context
    context = get_employee_context(employee_id)

    if not context["work_signals"]:
        print(f"❌ Employee {employee_id} not found in work signals data.")
        return

    employee = context["work_signals"]
    learner = context["learner_data"]

    # Determine certification target
    cert_target = certification or employee.get("current_certification_target", "AZ-204")
    cert_details = get_certification_details(cert_target)

    print("=" * 60)
    print(f"  STUDY PLAN GENERATOR - {employee_id}")
    print("=" * 60)
    print()
    print(f"  Employee: {employee_id} ({employee['role']})")
    print(f"  Team: {employee['team']}")
    print(f"  Target Certification: {cert_target}")
    print(f"  Meeting Hours/Week: {employee['meeting_hours_per_week']}")
    print(f"  Focus Hours/Week: {employee['focus_hours_per_week']}")
    print(f"  Preferred Slot: {employee['preferred_learning_slot']}")
    print(f"  Calendar Fragmentation: {employee['calendar_fragmentation_score']}")
    if learner:
        print(f"  Current Practice Score: {learner['practice_score_avg']}%")
        print(f"  Hours Studied So Far: {learner['hours_studied']}")
    print()

    # Build the request
    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    client = OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )

    system_prompt = build_system_prompt()

    user_message = f"""Create a personalized study plan for this employee:

EMPLOYEE PROFILE:
- Employee ID: {employee_id}
- Role: {employee['role']}
- Team: {employee['team']}
- Meeting hours/week: {employee['meeting_hours_per_week']}
- Focus hours available/week: {employee['focus_hours_per_week']}
- Deep work blocks/week: {employee['deep_work_blocks_per_week']}
- Preferred learning slot: {employee['preferred_learning_slot']}
- Calendar fragmentation: {employee['calendar_fragmentation_score']}
- Collaboration messages/day: {employee['avg_collaboration_messages_per_day']}

TARGET CERTIFICATION: {cert_target}
- Recommended total study hours: {cert_details['certification']['recommended_study_hours'] if cert_details['certification'] else 'Unknown'}
- Difficulty: {cert_details['certification']['difficulty_level'] if cert_details['certification'] else 'Unknown'}
- Prerequisites: {cert_details['certification']['prerequisites'] if cert_details['certification'] else []}
- Pass threshold: {cert_details['certification']['pass_threshold_pct'] if cert_details['certification'] else 70}%

{"CURRENT PROGRESS:" if learner else "NO PRIOR PROGRESS DATA"}
{f"- Practice score average: {learner['practice_score_avg']}%" if learner else ""}
{f"- Hours studied so far: {learner['hours_studied']}" if learner else ""}
{f"- Weeks in prep: {learner['weeks_in_prep']}" if learner else ""}
{f"- Study plan completion: {learner['study_plan_completion_pct']}%" if learner else ""}

Generate a concrete, week-by-week study plan with milestones and target scores.
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
        print(f"🤖 Study Plan Generator:\n\n{reply}")
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                reply = error_data["choices"][0]["message"]["content"]
                print(f"🤖 Study Plan Generator:\n\n{reply}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Study Plan Generator Agent")
    parser.add_argument("--employee", default="EMP-034", help="Employee ID (e.g., EMP-034)")
    parser.add_argument("--cert", default=None, help="Target certification (e.g., AZ-400)")
    args = parser.parse_args()

    run_study_plan(args.employee, args.cert)


if __name__ == "__main__":
    main()
