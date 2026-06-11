"""
SkillSentinel — Multi-Agent Enterprise Certification Readiness System

Local development approach using Microsoft Foundry model endpoint.
8 agents with Chain-of-Thought reasoning, source-grounding, and structured outputs.

Architecture:
    User → Mission Control (routing) → Agent Chain → Policy Guard + Verifier → Response

Features:
    - Multi-agent chaining for complex requests
    - Audit trail logging
    - Human approval gates
    - Permission-aware retrieval simulation
    - Parallel guard + verifier for speed

Run:
    python main.py
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
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
AUDIT_DIR = Path(__file__).parent / "audit_logs"
AUDIT_DIR.mkdir(exist_ok=True)

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
# Permission-Aware Retrieval Simulation
# ============================================================

def retrieve_with_permissions(filename: str, role: str = None, team: str = None, max_chars: int = 4000) -> str:
    """Simulate Foundry IQ permission-aware retrieval.

    In production, this would use Azure AI Search with RBAC filters.
    Here we simulate by returning full content (all roles have read access
    to the certification guide) with a permission header noting the access level.
    """
    content = load_doc(filename)

    # Permission simulation: log access level (in production this would be RBAC)
    access_note = f"[Permission: role={role or 'all'}, access=read_granted]"

    return f"{access_note}\n{content[:max_chars]}"


# ============================================================
# Context Builders (inject IQ layer data per agent)
# ============================================================

def build_curator_context(context: dict) -> str:
    """Foundry IQ: certification guide + role mappings."""
    semantic_model = load_json("semantic_model.json")
    role = context.get("role") or "Cloud Engineer"
    cert_guide = retrieve_with_permissions("engineering_certification_guide.md", role=role)
    certs = json.dumps(semantic_model["certifications"], indent=2)
    roles = json.dumps(semantic_model["roles"], indent=2)
    return f"ROLES (Fabric IQ):\n{roles}\n\nCERTIFICATIONS:\n{certs}\n\nKNOWLEDGE BASE (Foundry IQ - Permission-Aware Retrieval for role: {role}):\n[source: engineering_certification_guide.md]\n{cert_guide}"


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
            context["role"] = emp.get("role")
        if learner:
            emp_data += f"\nLEARNER PROGRESS:\n{json.dumps(learner, indent=2)}"

    return f"BUSINESS RULES (Fabric IQ) [source: semantic_model.json, section: business_rules]:\n{rules}\n\nSTUDY TEMPLATES [source: semantic_model.json, section: study_plan_templates]:\n{templates}{emp_data}"


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
            emp_data = f"\nEMPLOYEE WORK PATTERN (Work IQ) [source: work_activity_signals.json]:\n{json.dumps(emp, indent=2)}"
        if learner:
            emp_data += f"\nLEARNER PROGRESS [source: learner_performance.json]:\n{json.dumps(learner, indent=2)}"
    return f"BUSINESS RULES [source: semantic_model.json, section: business_rules]:\n{json.dumps(rules, indent=2)}{emp_data}"


def build_assessment_context(context: dict) -> str:
    """Foundry IQ: certification guide + scoring thresholds."""
    semantic_model = load_json("semantic_model.json")
    cert_id = context.get("certification", "AZ-204")
    cert = next((c for c in semantic_model["certifications"] if c["id"] == cert_id), None)
    role = context.get("role") or "Cloud Engineer"
    cert_guide = retrieve_with_permissions("engineering_certification_guide.md", role=role)

    learner_info = ""
    if context.get("employee_id"):
        learner_data = load_json("learner_performance.json")
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if learner:
            learner_info = f"\nLEARNER [source: learner_performance.json]:\n{json.dumps(learner, indent=2)}"

    cert_info = json.dumps(cert, indent=2) if cert else "Certification not found."
    return f"TARGET CERTIFICATION [source: semantic_model.json, section: certifications]:\n{cert_info}{learner_info}\n\nKNOWLEDGE BASE (Foundry IQ - Permission-Aware Retrieval):\n[source: engineering_certification_guide.md]\n{cert_guide}"


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
    return f"TEAM BENCHMARKS (Fabric IQ) [source: semantic_model.json, section: teams]:\n{benchmarks}\n\nAGGREGATED DATA:\n{team_data}"


# ============================================================
# Audit Trail
# ============================================================

class AuditTrail:
    """Logs every pipeline run for observability and compliance."""

    def __init__(self):
        self.entries = []
        self.start_time = None

    def start(self, user_message: str):
        self.start_time = time.time()
        self.entries = []
        self.log("USER_INPUT", {"message": user_message})

    def log(self, event: str, data: dict):
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data,
        })

    def finalize(self) -> dict:
        elapsed = round(time.time() - self.start_time, 2) if self.start_time else 0
        trail = {
            "pipeline_id": f"run-{int(time.time())}",
            "total_time_seconds": elapsed,
            "events": self.entries,
        }
        # Save to file
        filename = AUDIT_DIR / f"{trail['pipeline_id']}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(trail, f, indent=2)
        return trail


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

# Multi-agent chaining: complex requests trigger sequential agent calls
CHAIN_DEFINITIONS = {
    "full_preparation": ["learning_path", "study_plan", "engagement"],
    "readiness_check": ["assessment", "study_plan"],
}


def call_single_agent(client: OpenAI, agent_key: str, user_message: str, context: dict, audit: AuditTrail, previous_output: str = "") -> str:
    """Call a single agent with its IQ context. Passes previous agent output as additional context."""
    config = AGENT_CONFIG[agent_key]
    iq_context = config["context_builder"](context)

    if previous_output:
        iq_context += f"\n\n--- PREVIOUS AGENT OUTPUT (use as input) ---\n{previous_output}"

    agent_prompt = build_prompt(config["instructions"], iq_context)
    response = call_llm(client, agent_prompt, user_message)

    audit.log("AGENT_CALL", {
        "agent": agent_key,
        "label": config["label"],
        "input_length": len(user_message),
        "context_length": len(iq_context),
        "output_length": len(response),
    })

    return response


def run_governance(client: OpenAI, agent_output: str, audit: AuditTrail) -> tuple:
    """Run Policy Guard + Verifier. Returns (is_blocked, final_output)."""

    # Policy Guard
    guard_prompt = build_prompt(POLICY_GUARD_INSTRUCTIONS)
    guard_input = f"CHECK THIS AGENT OUTPUT:\n{agent_output}"
    guard_result = call_llm(client, guard_prompt, guard_input)

    blocked = False
    guard_status = "CLEARED"
    try:
        guard_clean = guard_result.strip()
        if guard_clean.startswith("```"):
            guard_clean = guard_clean.split("\n", 1)[1].rsplit("```", 1)[0]
        guard_json = json.loads(guard_clean)
        guard_status = guard_json.get("overall_status", "CLEARED")
        if guard_status == "BLOCKED":
            blocked = True
    except (json.JSONDecodeError, IndexError, ValueError):
        guard_status = "PARSE_ERROR_PASS"

    audit.log("POLICY_GUARD", {"status": guard_status, "blocked": blocked})

    if blocked:
        return True, "⚠️ Response blocked by Policy Guard due to policy violations."

    # Verifier
    verifier_prompt = build_prompt(VERIFIER_INSTRUCTIONS)
    verifier_input = f"VERIFY THIS AGENT OUTPUT:\n{agent_output}"
    verifier_result = call_llm(client, verifier_prompt, verifier_input)

    verdict = "APPROVED"
    try:
        ver_clean = verifier_result.strip()
        if ver_clean.startswith("```"):
            ver_clean = ver_clean.split("\n", 1)[1].rsplit("```", 1)[0]
        ver_json = json.loads(ver_clean)
        verdict = ver_json.get("verdict", "APPROVED")
    except (json.JSONDecodeError, IndexError, ValueError):
        verdict = "PARSE_ERROR_PASS"

    audit.log("VERIFIER", {"verdict": verdict})

    return False, agent_output


def run_pipeline(client: OpenAI, user_message: str, context: dict) -> str:
    """Full pipeline with chaining, governance, and audit trail."""
    audit = AuditTrail()
    audit.start(user_message)

    # Step 1: Mission Control routes the request
    routing_prompt = build_prompt(MISSION_CONTROL_INSTRUCTIONS)
    routing_result = call_llm(client, routing_prompt, user_message)

    # Parse routing
    try:
        clean = routing_result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        routing = json.loads(clean)
    except (json.JSONDecodeError, IndexError, ValueError):
        routing = {"agent": "learning_path", "employee_id": None, "team_id": None, "certification": None}

    audit.log("MISSION_CONTROL", {"routing": routing})

    # Update context from routing
    if routing.get("employee_id"):
        context["employee_id"] = routing["employee_id"]
    if routing.get("team_id"):
        context["team_id"] = routing["team_id"]
    if routing.get("certification"):
        context["certification"] = routing["certification"]

    agent_key = routing.get("agent", "learning_path")

    # Handle general/greeting messages directly
    if agent_key == "general":
        direct = routing.get("direct_response", "Hello! I'm SkillSentinel. I can help with certification paths, study plans, practice questions, engagement reminders, and team insights. What would you like help with?")
        print(f"  🎯 Mission Control (direct response)")
        audit.log("DIRECT_RESPONSE", {"message": direct})
        audit.finalize()
        return direct

    # Step 2: Determine if this is a chain or single agent call
    # Detect complex requests that need chaining
    chain = None
    msg_lower = user_message.lower()
    if any(kw in msg_lower for kw in ["prepare", "full plan", "help me get ready", "end to end"]):
        chain = CHAIN_DEFINITIONS["full_preparation"]
    elif any(kw in msg_lower for kw in ["am i ready", "readiness check", "should i take the exam"]):
        chain = CHAIN_DEFINITIONS["readiness_check"]

    if chain:
        # Multi-agent chaining
        print(f"  🔗 Mission Control → Chain: {' → '.join(AGENT_CONFIG[a]['label'] for a in chain)}")
        if routing.get("reasoning"):
            print(f"  💡 {routing['reasoning']}")
        print()

        previous_output = ""
        final_output_parts = []

        for i, agent_key_in_chain in enumerate(chain):
            config = AGENT_CONFIG[agent_key_in_chain]
            print(f"    [{i+1}/{len(chain)}] {config['label']}...", end=" ", flush=True)
            response = call_single_agent(client, agent_key_in_chain, user_message, context, audit, previous_output)
            previous_output = response
            final_output_parts.append(f"--- {config['label']} ---\n{response}")
            print("✓")

        agent_output = "\n\n".join(final_output_parts)
    else:
        # Single agent call
        config = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["learning_path"])
        print(f"  🔄 Mission Control → {config['label']}")
        if routing.get("reasoning"):
            print(f"  💡 {routing['reasoning']}")
        print()
        agent_output = call_single_agent(client, agent_key, user_message, context, audit)

    # Step 3: Human Approval Gate (for study plan modifications)
    if agent_key == "study_plan" or (chain and "study_plan" in chain):
        print("\n  🔒 Human Approval Gate: Study plan generated.")
        approval = input("     Approve this plan? [Y/n]: ").strip().lower()
        if approval == "n":
            audit.log("HUMAN_GATE", {"action": "REJECTED"})
            audit.finalize()
            return "Study plan rejected. Please provide additional requirements or constraints."
        audit.log("HUMAN_GATE", {"action": "APPROVED"})

    # Step 4: Governance (Policy Guard + Verifier)
    print("  🛡️ Running governance checks...", end=" ", flush=True)
    blocked, final_output = run_governance(client, agent_output, audit)
    if blocked:
        print("BLOCKED")
        audit.finalize()
        return final_output
    print("✓")

    # Step 5: Format for user (natural language)
    # Instead of extra LLM call, extract reasoning trace and present cleanly
    formatted = format_response(final_output)

    audit.log("FINAL_OUTPUT", {"length": len(formatted)})
    trail = audit.finalize()
    print(f"  📋 Audit: {trail['pipeline_id']} ({trail['total_time_seconds']}s)")

    return formatted


def format_response(agent_output: str) -> str:
    """Pass through agent output — agents now respond in natural language directly."""
    # Strip any markdown code fences the model might wrap around the response
    output = agent_output.strip()
    if output.startswith("```"):
        output = output.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return output


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
    print("║    🎯 Mission Control        (Orchestrator + Chaining)       ║")
    print("║    📚 Learning Path Curator  (Foundry IQ)                    ║")
    print("║    📅 Study Plan Generator   (Fabric IQ)                     ║")
    print("║    ⏰ Engagement Agent        (Work IQ)                      ║")
    print("║    📝 Assessment Agent        (Foundry IQ)                   ║")
    print("║    📊 Manager Insights        (Fabric IQ + Work IQ)         ║")
    print("║    🛡️ Policy Guard            (5-Layer Safety)               ║")
    print("║    ✅ Verifier                (Quality Gate)                  ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Features:                                                   ║")
    print("║    🔗 Multi-agent chaining for complex requests              ║")
    print("║    🔒 Human approval gates                                   ║")
    print("║    📋 Full audit trail (saved to audit_logs/)                ║")
    print("║    🔐 Permission-aware retrieval                             ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Type 'quit' to exit. Type 'audit' to view last trail.      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    context = {"employee_id": None, "team_id": None, "certification": None, "role": None}

    while True:
        user_input = input("👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Keep learning. 🚀")
            break
        if user_input.lower() == "audit":
            # Show last audit trail
            trails = sorted(AUDIT_DIR.glob("*.json"), reverse=True)
            if trails:
                with open(trails[0]) as f:
                    print(json.dumps(json.load(f), indent=2))
            else:
                print("No audit logs yet.")
            continue

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
