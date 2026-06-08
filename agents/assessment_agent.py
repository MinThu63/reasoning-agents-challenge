"""
Assessment Agent (Foundry IQ Grounded)

What it does:
- Generates credible, cited practice questions from approved content
- Scores/interprets readiness based on certification criteria
- Feeds results back into the planning loop
- Uses docs/ content (Foundry IQ) for grounded question generation
- Uses semantic_model.json (Fabric IQ) for scoring thresholds

Run standalone:
    python agents/assessment_agent.py

Test with specific cert:
    python agents/assessment_agent.py --cert AZ-400 --questions 5
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
DOCS_DIR = Path(__file__).parent.parent / "docs"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_doc(filename: str) -> str:
    with open(DOCS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt(certification: str) -> str:
    """Build the Assessment Agent's system prompt with grounded knowledge."""
    semantic_model = load_json("semantic_model.json")
    cert = next((c for c in semantic_model["certifications"] if c["id"] == certification), None)
    rules = semantic_model["business_rules"]

    # Load knowledge docs for grounding
    cert_guide = load_doc("engineering_certification_guide.md")

    return f"""You are the Assessment Agent for an enterprise learning and certification system.

YOUR ROLE:
You evaluate learner readiness by generating practice questions grounded in approved organizational knowledge.
You score responses and determine if a learner is ready for their certification exam.

WHAT YOU MUST DO:
1. Generate practice questions that are grounded in the company's certification guide and approved content
2. Questions must be realistic, scenario-based, and at the appropriate difficulty level
3. Each question must include the correct answer and a brief explanation
4. After presenting questions, assess overall readiness based on scoring thresholds
5. Recommend either "Ready for exam" or "Continue studying" with specific areas to focus on

TARGET CERTIFICATION: {certification}
{f"- Name: {cert['name']}" if cert else ""}
{f"- Skills assessed: {', '.join(cert['skills_assessed'])}" if cert else ""}
{f"- Difficulty: {cert['difficulty_level']}" if cert else ""}
{f"- Pass threshold: {cert['pass_threshold_pct']}%" if cert else ""}
{f"- Recommended practice score before exam: {cert['recommended_practice_score_before_exam']}%" if cert else ""}

BUSINESS RULES:
- Minimum practice score for exam approval: {rules['minimum_practice_score_for_exam_approval']}%
- Max consecutive practice failures before review: {rules['max_consecutive_practice_failures_before_review']}

GROUNDING SOURCE (Engineering Certification Guide):
{cert_guide[:3000]}

QUESTION REQUIREMENTS:
- Generate multiple-choice questions (4 options: A, B, C, D)
- Each question should test a different skill area from the certification
- Include scenario-based questions (not just definitions)
- Clearly mark the correct answer
- Provide a 1-2 sentence explanation for why the answer is correct
- At the end, provide a readiness assessment

All data is synthetic and for demonstration purposes only.
"""


def run_assessment(certification: str, num_questions: int = 5, employee_id: str = None):
    """Generate practice questions and assess readiness."""
    from openai import OpenAI

    # Get learner context if employee provided
    learner_context = ""
    if employee_id:
        learner_data = load_json("learner_performance.json")
        learner = next((l for l in learner_data if l.get("employee_id") == employee_id), None)
        if learner:
            learner_context = f"""
LEARNER CONTEXT:
- Employee: {employee_id}
- Role: {learner['role']}
- Team: {learner['team']}
- Current practice score average: {learner['practice_score_avg']}%
- Hours studied so far: {learner['hours_studied']}
- Weeks in prep: {learner['weeks_in_prep']}
- Study plan completion: {learner['study_plan_completion_pct']}%
"""

    print("=" * 60)
    print(f"  ASSESSMENT AGENT - {certification} Readiness Check")
    print("=" * 60)
    print()
    print(f"  Certification: {certification}")
    print(f"  Questions: {num_questions}")
    if employee_id:
        print(f"  Employee: {employee_id}")
    print()

    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    client = OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )

    system_prompt = build_system_prompt(certification)

    user_message = f"""Generate {num_questions} practice questions for the {certification} certification exam.

{learner_context}

Requirements:
1. Each question should test a DIFFERENT skill area
2. Use realistic Azure scenarios (not textbook definitions)
3. Format as multiple choice (A, B, C, D)
4. After all questions, provide:
   - The correct answers
   - Brief explanations
   - An overall READINESS ASSESSMENT (Ready / Not Ready / Borderline)
   - Specific areas to focus on if not ready
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
        print(f"🤖 Assessment Agent:\n\n{reply}")
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                reply = error_data["choices"][0]["message"]["content"]
                print(f"🤖 Assessment Agent:\n\n{reply}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Assessment Agent")
    parser.add_argument("--cert", default="AZ-400", help="Certification (e.g., AZ-400, AZ-204, DP-203)")
    parser.add_argument("--questions", type=int, default=5, help="Number of questions")
    parser.add_argument("--employee", default=None, help="Employee ID for context (e.g., EMP-034)")
    args = parser.parse_args()

    run_assessment(args.cert, args.questions, args.employee)


if __name__ == "__main__":
    main()
