"""
SkillSentinel — Streamlit Chat Interface

A web-based chat UI for the multi-agent certification readiness system.
Connects directly to the same pipeline as main.py.

Run locally:
    streamlit run streamlit_app.py

Deploy:
    Push to GitHub → Connect to Streamlit Cloud → Set secrets
"""

import streamlit as st
import json
import time
import os
from pathlib import Path
from io import StringIO
import sys

# Set env vars from Streamlit secrets FIRST (before any other imports)
try:
    if st.secrets:
        for key in ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_MODEL_DEPLOYMENT", "AZURE_AI_API_KEY",
                    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_INDEX"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
except Exception:
    pass  # No secrets file — use .env instead

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from agents.base import UNIVERSAL_SYSTEM_PROMPT, build_prompt
from agents.mission_control import INSTRUCTIONS as MISSION_CONTROL_INSTRUCTIONS
from agents.learning_path_curator import INSTRUCTIONS as CURATOR_INSTRUCTIONS
from agents.study_plan_generator import INSTRUCTIONS as STUDY_PLAN_INSTRUCTIONS
from agents.engagement_agent import INSTRUCTIONS as ENGAGEMENT_INSTRUCTIONS
from agents.assessment_agent import INSTRUCTIONS as ASSESSMENT_INSTRUCTIONS
from agents.manager_insights_agent import INSTRUCTIONS as MANAGER_INSTRUCTIONS
from agents.policy_guard import INSTRUCTIONS as POLICY_GUARD_INSTRUCTIONS
from agents.verifier import INSTRUCTIONS as VERIFIER_INSTRUCTIONS
from agents.tools import search_microsoft_learn, query_knowledge_base

# Import pipeline functions from main
from main import (
    get_client, call_llm, load_json, load_doc,
    build_curator_context, build_study_plan_context,
    build_engagement_context, build_assessment_context,
    build_manager_context, retrieve_with_permissions,
    AGENT_CONFIG, CHAIN_DEFINITIONS, format_response,
    call_single_agent, run_governance, AuditTrail
)

# ============================================================
# Page Config
# ============================================================

st.set_page_config(
    page_title="SkillSentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-checked.png", width=60)
    st.title("SkillSentinel")
    st.caption("Enterprise Certification Readiness System")

    st.divider()

    st.markdown("**8 Agents · 10 Reasoning Techniques**")
    st.markdown("""
    - 🎯 Mission Control (Router)
    - 📚 Learning Path Curator
    - 📅 Study Plan Generator
    - ⏰ Engagement Agent
    - 📝 Assessment Agent
    - 📊 Manager Insights
    - 🛡️ Policy Guard
    - ✅ Verifier
    """)

    st.divider()

    st.markdown("**Try these:**")
    example_prompts = [
        "What certs should a Cloud Engineer get?",
        "Create a study plan for EMP-034",
        "Help me prepare for AZ-204",
        "How is TEAM-D performing?",
        "Give me practice questions for AZ-400",
        "When should EMP-056 study this week?",
    ]
    for prompt in example_prompts:
        if st.button(prompt, key=f"btn_{prompt[:20]}", use_container_width=True):
            st.session_state["next_input"] = prompt
            st.rerun()

    st.divider()
    st.markdown("**IQ Layers:**")
    st.markdown("🟢 Foundry IQ (Azure AI Search) — Live")
    st.markdown("🟢 Fabric IQ (Semantic Model) — Active")
    st.markdown("🟢 Work IQ (Employee Signals) — Active")
    st.markdown("🟢 Microsoft Learn API — Live")

    st.divider()
    st.caption("Built for Microsoft AI Skills Fest · Agent League · Battle #2")


# ============================================================
# Main Chat Interface
# ============================================================

st.title("🛡️ SkillSentinel")
st.markdown("*Enterprise Certification Readiness System — Reasoning Agents with Microsoft Foundry*")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = {"employee_id": None, "team_id": None, "certification": None, "role": None}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🛡️"):
        st.markdown(message["content"])
        if "metadata" in message:
            with st.expander("📋 Pipeline Details", expanded=False):
                st.json(message["metadata"])


# ============================================================
# Pipeline (adapted for Streamlit)
# ============================================================

def run_streamlit_pipeline(user_message: str) -> dict:
    """Run the full pipeline and return response + metadata."""
    client = get_client()
    context = st.session_state.context
    audit = AuditTrail()
    audit.start(user_message)
    metadata = {"agents_called": [], "pipeline_steps": []}

    # Pre-check greetings
    greeting_patterns = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                         "what can you do", "who are you", "thanks", "thank you", "bye"]
    if user_message.strip().lower().rstrip("!?.") in greeting_patterns or len(user_message.strip()) < 4:
        metadata["pipeline_steps"].append("🎯 Greeting detected (local pattern match)")
        return {
            "response": "Hello! I'm SkillSentinel. I can help with:\n- **Certification paths** — \"What certs for a Cloud Engineer?\"\n- **Study plans** — \"Create a plan for EMP-034\"\n- **Practice questions** — \"Quiz me on AZ-400\"\n- **Engagement reminders** — \"When should EMP-056 study?\"\n- **Team insights** — \"How is TEAM-D doing?\"\n\nWhat would you like help with?",
            "metadata": metadata,
        }

    # Step 1: Route
    metadata["pipeline_steps"].append("🎯 Mission Control: classifying intent...")
    routing_prompt = build_prompt(MISSION_CONTROL_INSTRUCTIONS)
    routing_result = call_llm(client, routing_prompt, user_message)

    try:
        clean = routing_result.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        routing = json.loads(clean)
    except (json.JSONDecodeError, IndexError, ValueError):
        routing = {"agent": "learning_path", "employee_id": None, "team_id": None, "certification": None, "confidence": 0.5}

    # Update context
    if routing.get("employee_id"):
        context["employee_id"] = routing["employee_id"]
    if routing.get("team_id"):
        context["team_id"] = routing["team_id"]
    if routing.get("certification"):
        context["certification"] = routing["certification"]

    agent_key = routing.get("agent", "learning_path")
    confidence = routing.get("confidence", 1.0)
    metadata["routing"] = routing

    # Handle general
    if agent_key == "general":
        direct = routing.get("direct_response", "I can help with certification paths, study plans, practice questions, reminders, and team insights. What would you like?")
        metadata["pipeline_steps"].append("🎯 Mission Control: direct response (general)")
        return {"response": direct, "metadata": metadata}

    # Handle low confidence
    if isinstance(confidence, (int, float)) and confidence < 0.6:
        metadata["pipeline_steps"].append(f"⚠️ Low confidence ({confidence}) — requesting clarification")
        return {"response": "I'm not quite sure what you need. Could you clarify? I can help with:\n- Certification recommendations\n- Study plans\n- Practice questions\n- Reminders\n- Team progress", "metadata": metadata}

    # Step 2: Chain or single agent
    chain = None
    msg_lower = user_message.lower()
    if any(kw in msg_lower for kw in ["prepare", "full plan", "help me get ready", "end to end"]):
        chain = CHAIN_DEFINITIONS["full_preparation"]
    elif any(kw in msg_lower for kw in ["am i ready", "readiness check", "should i take the exam"]):
        chain = CHAIN_DEFINITIONS["readiness_check"]

    if chain:
        metadata["pipeline_steps"].append(f"🔗 Chain: {' → '.join(AGENT_CONFIG[a]['label'] for a in chain)}")
        previous_output = ""
        final_parts = []
        for agent_key_in_chain in chain:
            config = AGENT_CONFIG[agent_key_in_chain]
            metadata["agents_called"].append(config["label"])
            metadata["pipeline_steps"].append(f"  ↳ Calling {config['label']}...")
            response = call_single_agent(client, agent_key_in_chain, user_message, context, audit, previous_output)
            previous_output = response
            final_parts.append(f"**{config['label']}:**\n\n{response}")
        agent_output = "\n\n---\n\n".join(final_parts)
    else:
        config = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["learning_path"])
        metadata["agents_called"].append(config["label"])
        metadata["pipeline_steps"].append(f"🔄 Routing → {config['label']}")
        agent_output = call_single_agent(client, agent_key, user_message, context, audit)

    # Step 3: Governance
    metadata["pipeline_steps"].append("🛡️ Policy Guard + Verifier...")
    blocked, final_output = run_governance(client, agent_output, agent_key, user_message, context, audit)
    if blocked:
        metadata["pipeline_steps"].append("❌ BLOCKED by Policy Guard")
        return {"response": "⚠️ Response blocked by Policy Guard due to policy violations.", "metadata": metadata}

    metadata["pipeline_steps"].append("✅ Governance passed")

    # Format
    formatted = format_response(final_output)
    trail = audit.finalize()
    metadata["audit_id"] = trail["pipeline_id"]
    metadata["total_time"] = trail["total_time_seconds"]

    return {"response": formatted, "metadata": metadata}


# ============================================================
# Chat Input
# ============================================================

# Get input from either chat box or sidebar button
prompt = st.chat_input("Ask SkillSentinel anything about certifications...")

# If a sidebar button was clicked, use that instead
if "next_input" in st.session_state:
    prompt = st.session_state.pop("next_input")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("Reasoning..."):
            start = time.time()
            result = run_streamlit_pipeline(prompt)
            elapsed = round(time.time() - start, 1)

        st.markdown(result["response"])

        # Show pipeline details
        with st.expander(f"📋 Pipeline Details ({elapsed}s)", expanded=False):
            for step in result["metadata"].get("pipeline_steps", []):
                st.markdown(f"  {step}")
            if result["metadata"].get("agents_called"):
                st.markdown(f"  **Agents:** {', '.join(result['metadata']['agents_called'])}")
            if result["metadata"].get("audit_id"):
                st.markdown(f"  **Audit:** `{result['metadata']['audit_id']}`")

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "metadata": result["metadata"],
    })
