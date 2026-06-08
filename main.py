"""
Multi-Agent Enterprise Learning System - Orchestrator

This is the main entry point that connects all 5 agents into a single
interactive conversation. The Dispatcher analyzes each user message and
routes it to the correct specialized agent.

Run with:
    python main.py

Architecture:
    User Message → Dispatcher (routing) → Specialized Agent → Response
                                        ↓
    Agents: Study Plan Generator | Assessment | Engagement | Manager Insights | Curator

Connected to: Azure AI Foundry (project 24036948-0730, model gpt-oss-120b)
IQ Layers: Fabric IQ (semantic_model.json), Work IQ (work_activity_signals.json), Foundry IQ (docs/)
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-oss-120b")
API_KEY = os.getenv("AZURE_AI_API_KEY", "")

DATA_DIR = Path(__file__).parent / "data"
DOCS_DIR = Path(__file__).parent / "docs"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_doc(filename: str) -> str:
    with open(DOCS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def get_client():
    from openai import OpenAI
    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    return OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )


def call_llm(client, system_prompt: str, messages: list) -> str:
    """Call the LLM and handle content_filter responses."""
    # Add formatting instruction to keep terminal output readable
    format_rule = "\n\nFORMATTING: You are responding in a terminal. Do NOT use markdown tables. Use bullet points, numbered lists, and plain text instead. Keep formatting simple and readable in a plain text console."
    full_messages = [{"role": "system", "content": system_prompt + format_rule}] + messages
    try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=full_messages,
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
                return f"Error: {e}"
        return f"Error: {e}"


# ============================================================
# DISPATCHER - Routes messages to the correct agent
# ============================================================

DISPATCHER_PROMPT = """You are the Dispatcher for a multi-agent enterprise learning system.

Your ONLY job is to classify user messages and return a JSON routing decision.
You do NOT answer the user's question. You ONLY route it.

Return EXACTLY one JSON object (no markdown, no explanation):
{
  "agent": "study_plan" | "assessment" | "engagement" | "manager_insights" | "curator",
  "employee_id": "EMP-XXX" or null,
  "team_id": "TEAM-X" or null,
  "certification": "XX-XXX" or null,
  "reasoning": "one sentence why this agent"
}

ROUTING RULES:
- "study_plan" → user wants a study schedule, timeline, weekly plan, or asks about preparation steps
- "assessment" → user wants practice questions, readiness check, quiz, or exam evaluation
- "engagement" → user asks about reminders, motivation, when to study, work-life balance, or focus time
- "manager_insights" → user is a manager asking about team progress, pass rates, risk areas, or aggregate data
- "curator" → user asks for learning resources, recommendations, what to study, or certification requirements

EMPLOYEE DETECTION:
- If user mentions "EMP-XXX" or "L-XXXX", extract the employee_id
- If user says "I'm on TEAM-X" or "my team", extract team_id
- If user mentions a certification code (AZ-204, AZ-400, DP-203, etc.), extract it

EXAMPLES:
- "Create a study plan for me" → {"agent": "study_plan", ...}
- "Give me practice questions for AZ-400" → {"agent": "assessment", ...}
- "When should I study this week?" → {"agent": "engagement", ...}
- "How is TEAM-B doing?" → {"agent": "manager_insights", ...}
- "What cert should a Cloud Engineer get?" → {"agent": "curator", ...}
"""


def route_message(client, user_message: str, context: dict) -> dict:
    """Use the dispatcher to classify and route the message."""
    messages = [{"role": "user", "content": user_message}]

    # Add context from previous turns
    if context.get("employee_id"):
        messages[0]["content"] += f"\n[Context: employee={context['employee_id']}, team={context.get('team_id', '')}, cert={context.get('certification', '')}]"

    result = call_llm(client, DISPATCHER_PROMPT, messages)

    # Parse JSON from response
    try:
        # Clean up potential markdown wrapping
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1].rsplit("```", 1)[0]
        routing = json.loads(result)
    except json.JSONDecodeError:
        # Fallback routing
        routing = {"agent": "curator", "employee_id": None, "team_id": None, "certification": None, "reasoning": "Could not parse routing"}

    return routing


# ============================================================
# SPECIALIZED AGENTS
# ============================================================

def run_study_plan_agent(client, user_message: str, context: dict) -> str:
    """Study Plan Generator - Fabric IQ grounded."""
    semantic_model = load_json("semantic_model.json")
    rules = semantic_model["business_rules"]

    # Get employee data if available
    employee_context = ""
    if context.get("employee_id"):
        work_signals = load_json("work_activity_signals.json")
        learner_data = load_json("learner_performance.json")
        emp = next((e for e in work_signals if e["employee_id"] == context["employee_id"]), None)
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if emp:
            employee_context = f"""
EMPLOYEE DATA (from Fabric IQ / Work IQ):
- ID: {emp['employee_id']} | Role: {emp['role']} | Team: {emp['team']}
- Meeting hours/week: {emp['meeting_hours_per_week']}
- Focus hours/week: {emp['focus_hours_per_week']}
- Deep work blocks: {emp['deep_work_blocks_per_week']}
- Preferred slot: {emp['preferred_learning_slot']}
- Calendar fragmentation: {emp['calendar_fragmentation_score']}
"""
        if learner:
            employee_context += f"""- Practice score: {learner['practice_score_avg']}%
- Hours studied: {learner['hours_studied']} | Weeks in prep: {learner['weeks_in_prep']}
- Plan completion: {learner['study_plan_completion_pct']}%
"""

    system_prompt = f"""You are the Study Plan Generator Agent (Fabric IQ Grounded).
You create personalized, capacity-aware study plans.

BUSINESS RULES:
- Optimal meetings: {rules['optimal_meeting_hours_range'][0]}-{rules['optimal_meeting_hours_range'][1]} hrs/week
- Study target: {rules['optimal_study_hours_per_week'][0]}-{rules['optimal_study_hours_per_week'][1]} hrs/week
- Critical threshold: >{rules['critical_meeting_threshold']} hrs/week = at risk
- Min practice score for exam: {rules['minimum_practice_score_for_exam_approval']}%

STUDY TEMPLATES:
{json.dumps(semantic_model['study_plan_templates'], indent=2)}

{employee_context}

Create concrete week-by-week plans with milestones. Flag workload risks. Be practical.
All data is synthetic."""

    messages = [{"role": "user", "content": user_message}]
    return call_llm(client, system_prompt, messages)


def run_assessment_agent(client, user_message: str, context: dict) -> str:
    """Assessment Agent - Foundry IQ grounded."""
    semantic_model = load_json("semantic_model.json")
    cert_id = context.get("certification", "AZ-204")
    cert = next((c for c in semantic_model["certifications"] if c["id"] == cert_id), None)

    # Load docs for grounding
    cert_guide = load_doc("engineering_certification_guide.md")[:2000]

    employee_context = ""
    if context.get("employee_id"):
        learner_data = load_json("learner_performance.json")
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if learner:
            employee_context = f"""
LEARNER: {learner['employee_id']} | Score: {learner['practice_score_avg']}% | Hours: {learner['hours_studied']}
"""

    system_prompt = f"""You are the Assessment Agent (Foundry IQ Grounded).
You generate practice questions and evaluate readiness.

TARGET: {cert_id} - {cert['name'] if cert else 'Unknown'}
Skills: {', '.join(cert['skills_assessed']) if cert else 'General'}
Pass threshold: {cert['pass_threshold_pct'] if cert else 70}%
Recommended practice score: {cert['recommended_practice_score_before_exam'] if cert else 80}%
{employee_context}

GROUNDING (from knowledge base):
{cert_guide}

Generate scenario-based multiple-choice questions. Provide answers, explanations, and readiness assessment.
All data is synthetic."""

    messages = [{"role": "user", "content": user_message}]
    return call_llm(client, system_prompt, messages)


def run_engagement_agent(client, user_message: str, context: dict) -> str:
    """Engagement Agent - Work IQ grounded."""
    semantic_model = load_json("semantic_model.json")
    rules = semantic_model["business_rules"]

    employee_context = ""
    if context.get("employee_id"):
        work_signals = load_json("work_activity_signals.json")
        learner_data = load_json("learner_performance.json")
        emp = next((e for e in work_signals if e["employee_id"] == context["employee_id"]), None)
        learner = next((l for l in learner_data if l.get("employee_id") == context["employee_id"]), None)
        if emp:
            employee_context = f"""
WORK PATTERN (Work IQ):
- Meetings: {emp['meeting_hours_per_week']} hrs/week | Focus: {emp['focus_hours_per_week']} hrs/week
- Deep work blocks: {emp['deep_work_blocks_per_week']} | Preferred: {emp['preferred_learning_slot']}
- Fragmentation: {emp['calendar_fragmentation_score']} | Messages/day: {emp['avg_collaboration_messages_per_day']}
"""
        if learner:
            employee_context += f"- Progress: {learner['study_plan_completion_pct']}% complete | Score: {learner['practice_score_avg']}%\n"

    system_prompt = f"""You are the Engagement Agent (Work IQ Grounded).
You keep learners on track with personalized, context-aware reminders.

RULES:
- Critical meeting threshold: >{rules['critical_meeting_threshold']} hrs/week
- Focus hour target: {rules['focus_hour_utilization_target_pct']}%
- Never remind during peak collaboration hours
- Be warm and supportive, never pushy
{employee_context}

Suggest specific reminder times, adapt tone to workload, celebrate small wins.
All data is synthetic."""

    messages = [{"role": "user", "content": user_message}]
    return call_llm(client, system_prompt, messages)


def run_manager_insights_agent(client, user_message: str, context: dict) -> str:
    """Manager Insights Agent - Work IQ + Fabric IQ grounded."""
    learner_data = load_json("learner_performance.json")
    work_signals = load_json("work_activity_signals.json")
    semantic_model = load_json("semantic_model.json")

    team_id = context.get("team_id")

    # Aggregate data
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

        data_summary = f"""
TEAM DATA (aggregated, no individual names):
- Team: {team_id or 'All Teams'} | Learners: {total}
- Pass rate: {round(passed/total*100, 1)}% | Avg score: {avg_score}%
- Avg meetings: {avg_meetings} hrs/week | At-risk: {at_risk}/{len(workers)}
"""
    else:
        data_summary = "No team data available."

    system_prompt = f"""You are the Manager Insights Agent (Work IQ + Fabric IQ Grounded).
You provide team-level visibility without exposing individual data.

BENCHMARKS:
{json.dumps(semantic_model['teams'], indent=2)}

RULES:
- Optimal meetings: 12-16 hrs/week | Critical: >20 hrs/week
- Target practice score: ≥80% | Focus target: 75%
- NEVER expose individual names or personal scores
- Use aggregates only (averages, percentages, counts)
{data_summary}

Provide executive summaries, risk analysis, and actionable recommendations.
All data is synthetic."""

    messages = [{"role": "user", "content": user_message}]
    return call_llm(client, system_prompt, messages)


def run_curator_agent(client, user_message: str, context: dict) -> str:
    """Learning Path Curator - Foundry IQ grounded."""
    semantic_model = load_json("semantic_model.json")
    cert_guide = load_doc("engineering_certification_guide.md")[:3000]

    cert_list = [
        {"id": c["id"], "name": c["name"], "skills": c["skills_assessed"],
         "hours": c["recommended_study_hours"], "prereqs": c["prerequisites"]}
        for c in semantic_model["certifications"]
    ]

    system_prompt = f"""You are the Learning Path Curator Agent (Foundry IQ Grounded).
You suggest relevant learning paths and resources based on the learner's role and goals.

ROLE-CERTIFICATION MAPPING:
{json.dumps(semantic_model['roles'], indent=2)}

CERTIFICATION DETAILS:
{json.dumps(cert_list, indent=2)}

KNOWLEDGE BASE CONTENT (Foundry IQ):
{cert_guide}

IMPORTANT RULES:
- When citing resources, reference internal documents by filename (e.g., "Source: engineering_certification_guide.md")
- Do NOT invent external URLs or fake links
- If recommending external study, say "Refer to Microsoft Learn official modules" without fabricating specific URLs
- Always mention prerequisites before recommending advanced certs
- Include estimated study hours from the certification details above

Map certifications to roles, suggest prerequisite paths, recommend resources.
All data is synthetic."""

    messages = [{"role": "user", "content": user_message}]
    return call_llm(client, system_prompt, messages)


# ============================================================
# AGENT ROUTING MAP
# ============================================================

AGENT_MAP = {
    "study_plan": ("📅 Study Plan Generator", run_study_plan_agent),
    "assessment": ("📝 Assessment Agent", run_assessment_agent),
    "engagement": ("⏰ Engagement Agent", run_engagement_agent),
    "manager_insights": ("📊 Manager Insights", run_manager_insights_agent),
    "curator": ("📚 Learning Path Curator", run_curator_agent),
}


# ============================================================
# MAIN INTERACTIVE LOOP
# ============================================================

def main():
    client = get_client()

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  MULTI-AGENT ENTERPRISE LEARNING SYSTEM                     ║")
    print("║  Connected to: Azure AI Foundry (24036948-0730)             ║")
    print("║  Model: gpt-oss-120b                                        ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Agents:                                                     ║")
    print("║    📚 Learning Path Curator    (Foundry IQ)                  ║")
    print("║    📅 Study Plan Generator     (Fabric IQ)                   ║")
    print("║    ⏰ Engagement Agent          (Work IQ)                    ║")
    print("║    📝 Assessment Agent          (Foundry IQ)                 ║")
    print("║    📊 Manager Insights          (Work IQ + Fabric IQ)       ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  Type your message. The Dispatcher routes automatically.    ║")
    print("║  Type 'quit' to exit.                                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Conversation context (persists across turns)
    context = {
        "employee_id": None,
        "team_id": None,
        "certification": None,
    }

    while True:
        user_input = input("👤 You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Keep learning. 🚀")
            break

        # Step 1: Route the message
        print("\n  🔄 Dispatcher routing...", end=" ")
        routing = route_message(client, user_input, context)

        # Update context from routing
        if routing.get("employee_id"):
            context["employee_id"] = routing["employee_id"]
        if routing.get("team_id"):
            context["team_id"] = routing["team_id"]
        if routing.get("certification"):
            context["certification"] = routing["certification"]

        agent_key = routing.get("agent", "curator")
        agent_name, agent_fn = AGENT_MAP.get(agent_key, AGENT_MAP["curator"])

        print(f"→ {agent_name}")
        print(f"  💡 Reason: {routing.get('reasoning', 'N/A')}")
        print()

        # Step 2: Call the specialized agent
        response = agent_fn(client, user_input, context)

        print(f"🤖 {agent_name}:\n")
        print(response)
        print()
        print("─" * 60)
        print()


if __name__ == "__main__":
    main()
