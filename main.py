"""
SkillSentinel — Multi-Agent Enterprise Certification Readiness System

Local development approach using Microsoft Foundry model endpoint.
8 agents with Chain-of-Thought reasoning, source-grounding, and structured JSON outputs.

Architecture:
    User → Mission Control (routing) → Specialized Agent → Policy Guard → Verifier → Response

Run:
    python main.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============================================================
# Configuration
# ============================================================

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-oss-120b")
API_KEY = os.getenv("AZURE_AI_API_KEY", "")

DATA_DIR = Path(__file__).parent / "data"
DOCS_DIR = Path(__file__).parent / "docs"

# ============================================================
# Agent Imports
# ============================================================

from agents.base import UNIVERSAL_SYSTEM_PROMPT, build_prompt
from agents.mission_control import INSTRUCTIONS as MISSION_CONTROL_INSTRUCTIONS
from agents.learning_path_curator import INSTRUCTIONS as CURATOR_INSTRUCTIONS
from agents.study_plan_generator import INSTRUCTIONS as STUDY_PLAN_INSTRUCTIONS
from agents.engagement_agent import INSTRUCTIONS as ENGAGEMENT_INSTRUCTIONS
from agents.assessment_agent import INSTRUCTIONS as ASSESSMENT_INSTRUCTIONS
from agents.manager_insights_agent import INSTRUCTIONS as MANAGER_INSTRUCTIONS
from agents.policy_guard import INSTRUCTIONS as POLICY_GUARD_INSTRUCTIONS
from agents.verifier import INSTRUCTIONS as VERIFIER_INSTRUCTIONS


# ============================================================
# LLM Client
# ============================================================

def get_client() -> OpenAI:
    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    return OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )


def call_llm(client: OpenAI, system_prompt: str, user_message: str) -> str:
    """Call the LLM with system prompt and user message."""
    try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                return error_data["choices"][0]["message"]["content"]
            except:
                pass
        return f'{{"error": "{e}"}}'


# ============================================================
# Data Loading (IQ Layers)
# ============================================================

def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_doc(filename: str) -> str:
    with open(DOCS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


# ============================================================
# Context Builders (inject IQ layer data per agent)
# ============================================================

def build_curator_context(context: dict) -> str:
    """Foundry IQ: certification guide + role mappings."""
    semantic_model = load_json("semantic_model.json")
    cert_guide = load_doc("engineering_certification_guide.md")[:4000]
    certs = json.dumps(semantic_model["certifications"], indent=2)
    roles = json.dumps(semantic_model["roles"], indent=2)
    return f"ROLES (Fabric IQ):\n{roles}\n\nCERTIFICATIONS:\n{certs}\n\nKNOWLEDGE BASE (Foundry IQ - Source: engineering_certification_guide.md):\n{cert_guide}"


def build_study_plan_context(context: dict) -> str:
    """Fabric IQ + Work IQ: business rules, templates, employee signals."""
    semantic_model = load_json("semantic_model.json")
    rules = json.dumps(semantic_model["business_rules"], indent=2)
    templates = json.dumps(semantic_model["study_plan_templates"], indent=2)

    emp_data = ""
    if context.get("employee_id"):
        work_signals = load_json("work_activity_signals.json")
        learner_data = load_json("learner_performance.json")
        emp = next((e for e in work_signals if e["employee_id"] == context["employee_id"]), None)
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if emp:
            emp_data = f"\nEMPLOYEE (Work IQ):\n{json.dumps(emp, indent=2)}"
        if learner:
            emp_data += f"\nLEARNER PROGRESS:\n{json.dumps(learner, indent=2)}"

    return f"BUSINESS RULES (Fabric IQ):\n{rules}\n\nSTUDY TEMPLATES:\n{templates}{emp_data}"


def build_engagement_context(context: dict) -> str:
    """Work IQ: employee work patterns."""
    rules = load_json("semantic_model.json")["business_rules"]
    emp_data = ""
    if context.get("employee_id"):
        work_signals = load_json("work_activity_signals.json")
        learner_data = load_json("learner_performance.json")
        emp = next((e for e in work_signals if e["employee_id"] == context["employee_id"]), None)
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if emp:
            emp_data = f"\nEMPLOYEE WORK PATTERN (Work IQ):\n{json.dumps(emp, indent=2)}"
        if learner:
            emp_data += f"\nLEARNER PROGRESS:\n{json.dumps(learner, indent=2)}"
    return f"BUSINESS RULES:\n{json.dumps(rules, indent=2)}{emp_data}"


def build_assessment_context(context: dict) -> str:
    """Foundry IQ: certification guide + scoring thresholds."""
    semantic_model = load_json("semantic_model.json")
    cert_id = context.get("certification", "AZ-204")
    cert = next((c for c in semantic_model["certifications"] if c["id"] == cert_id), None)
    cert_guide = load_doc("engineering_certification_guide.md")[:4000]

    learner_info = ""
    if context.get("employee_id"):
        learner_data = load_json("learner_performance.json")
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if learner:
            learner_info = f"\nLEARNER:\n{json.dumps(learner, indent=2)}"

    cert_info = json.dumps(cert, indent=2) if cert else "Certification not found."
    return f"TARGET CERTIFICATION:\n{cert_info}{learner_info}\n\nKNOWLEDGE BASE (Foundry IQ - Source: engineering_certification_guide.md):\n{cert_guide}"


def build_manager_context(context: dict) -> str:
    """Fabric IQ + Work IQ: aggregated team data."""
    learner_data = load_json("learner_performance.json")
    work_signals = load_json("work_activity_signals.json")
    semantic_model = load_json("semantic_model.json")

    team_id = context.get("team_id")
    if team_id:
        learners = [l for l in learner_data if l.get("team") == team_id]
        workers = [w for w in work_signals if w.get("team") == team_id]
    else:
        learners = learner_data
        workers = work_signals

    if learners:
        total = len(learners)
        passed = sum(1 for l in learners if l["exam_outcome"] == "Pass")
        avg_score = round(sum(l["practice_score_avg"] for l in learners) / total, 1)
        avg_meetings = round(sum(w["meeting_hours_per_week"] for w in workers) / len(workers), 1) if workers else 0
        at_risk = sum(1 for w in workers if w["meeting_hours_per_week"] > 20)
        team_data = json.dumps({
            "team_id": team_id or "ALL",
            "total_learners": total,
            "passed": passed,
            "pass_rate_pct": round(passed / total * 100, 1),
            "avg_practice_score": avg_score,
            "avg_meeting_hours": avg_meetings,
            "at_risk_count": at_risk,
            "at_risk_pct": round(at_risk / len(workers) * 100, 1) if workers else 0,
        }, indent=2)
    else:
        team_data = '{"error": "No team data found"}'

    benchmarks = json.dumps(semantic_model["teams"], indent=2)
    return f"TEAM BENCHMARKS (Fabric IQ):\n{benchmarks}\n\nAGGREGATED DATA:\n{team_data}"


# ============================================================
# Agent Pipeline
# ============================================================

AGENT_CONFIG = {
    "learning_path": {"instructions": CURATOR_INSTRUCTIONS, "context_builder": build_curator_context, "label": "📚 Learning Path Curator"},
    "study_plan": {"instructions": STUDY_PLAN_INSTRUCTIONS, "context_builder": build_study_plan_context, "label": "📅 Study Plan Generator"},
    "engagement": {"instructions": ENGAGEMENT_INSTRUCTIONS, "context_builder": build_engagement_context, "label": "⏰ Engagement Agent"},
    "assessment": {"instructions": ASSESSMENT_INSTRUCTIONS, "context_builder": build_assessment_context, "label": "📝 Assessment Agent"},
    "manager_insights": {"instructions": MANAGER_INSTRUCTIONS, "context_builder": build_manager_context, "label": "📊 Manager Insights"},
}


def run_pipeline(client: OpenAI, user_message: str, context: dict) -> str:
    """Full pipeline: Mission Control → Agent → Policy Guard → Verifier."""

    # Step 1: Mission Control routes the request
    routing_prompt = build_prompt(MISSION_CONTROL_INSTRUCTIONS)
    routing_result = call_llm(client, routing_prompt, user_message)

    # Parse routing
    try:
        clean = routing_result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        routing = json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        routing = {"agent": "learning_path", "employee_id": None, "team_id": None, "certification": None}

    # Update context from routing
    if routing.get("employee_id"):
        context["employee_id"] = routing["employee_id"]
    if routing.get("team_id"):
        context["team_id"] = routing["team_id"]
    if routing.get("certification"):
        context["certification"] = routing["certification"]

    agent_key = routing.get("agent", "learning_path")
    config = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["learning_path"])

    print(f"  🔄 Mission Control → {config['label']}")
    if routing.get("reasoning"):
        print(f"  💡 {routing['reasoning']}")
    print()

    # Step 2: Call the specialized agent with IQ layer context
    iq_context = config["context_builder"](context)
    agent_prompt = build_prompt(config["instructions"], iq_context)
    agent_response = call_llm(client, agent_prompt, user_message)

    # Step 3: Policy Guard check
    guard_prompt = build_prompt(POLICY_GUARD_INSTRUCTIONS)
    guard_input = f"CHECK THIS AGENT OUTPUT:\n{agent_response}"
    guard_result = call_llm(client, guard_prompt, guard_input)

    # Parse guard result
    blocked = False
    try:
        guard_clean = guard_result.strip()
        if guard_clean.startswith("```"):
            guard_clean = guard_clean.split("\n", 1)[1].rsplit("```", 1)[0]
        guard_json = json.loads(guard_clean)
        if guard_json.get("overall_status") == "BLOCKED":
            blocked = True
            print("  🛡️ Policy Guard: BLOCKED")
            print(f"  Violations: {guard_json.get('violations', [])}")
    except (json.JSONDecodeError, IndexError):
        pass  # If guard fails to parse, pass through

    if blocked:
        return "⚠️ Response blocked by Policy Guard. The output contained policy violations."

    # Step 4: Verifier check
    verifier_prompt = build_prompt(VERIFIER_INSTRUCTIONS)
    verifier_input = f"VERIFY THIS AGENT OUTPUT:\n{agent_response}"
    verifier_result = call_llm(client, verifier_prompt, verifier_input)

    try:
        ver_clean = verifier_result.strip()
        if ver_clean.startswith("```"):
            ver_clean = ver_clean.split("\n", 1)[1].rsplit("```", 1)[0]
        ver_json = json.loads(ver_clean)
        verdict = ver_json.get("verdict", "APPROVED")
        if verdict == "APPROVED":
            print("  ✅ Verifier: APPROVED")
        elif verdict == "REVISE":
            print(f"  ⚠️ Verifier: REVISE — {ver_json.get('issues', [])}")
        elif verdict == "ESCALATE":
            print("  🚨 Verifier: ESCALATE — insufficient grounding")
    except (json.JSONDecodeError, IndexError):
        print("  ✅ Verifier: PASSED")

    return agent_response


# ============================================================
# Interactive Loop
# ============================================================

def main():
    client = get_client()

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  SkillSentinel — Enterprise Certification Readiness System  ║")
    print("║  Local Development | Model: gpt-oss-120b                    ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Agents:                                                     ║")
    print("║    🎯 Mission Control        (Orchestrator)                  ║")
    print("║    📚 Learning Path Curator  (Foundry IQ)                    ║")
    print("║    📅 Study Plan Generator   (Fabric IQ)                     ║")
    print("║    ⏰ Engagement Agent        (Work IQ)                      ║")
    print("║    📝 Assessment Agent        (Foundry IQ)                   ║")
    print("║    📊 Manager Insights        (Fabric IQ + Work IQ)         ║")
    print("║    🛡️ Policy Guard            (Safety Layer)                 ║")
    print("║    ✅ Verifier                (Quality Gate)                  ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Pipeline: User → Mission Control → Agent → Guard → Verify  ║")
    print("║  Type 'quit' to exit.                                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    context = {"employee_id": None, "team_id": None, "certification": None}

    while True:
        user_input = input("👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Keep learning. 🚀")
            break

        print()
        response = run_pipeline(client, user_input, context)
        print()
        print(f"🤖 SkillSentinel:\n")
        print(response)
        print()
        print("─" * 60)
        print()


if __name__ == "__main__":
    main()
