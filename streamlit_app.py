"""
Fabric 365 — Streamlit Chat Interface

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

# Set env vars from Streamlit secrets FIRST (before any other imports)
try:
    if st.secrets:
        for key in ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_MODEL_DEPLOYMENT", "AZURE_AI_API_KEY",
                    "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_SEARCH_INDEX"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
except Exception:
    pass

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
    page_title="Fabric 365",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom CSS
# ============================================================

st.markdown("""
<style>
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85em;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .badge-curator { background: #e3f2fd; color: #1565c0; }
    .badge-plan { background: #e8f5e9; color: #2e7d32; }
    .badge-engage { background: #fff3e0; color: #e65100; }
    .badge-assess { background: #fce4ec; color: #c62828; }
    .badge-manager { background: #f3e5f5; color: #6a1b9a; }
    .badge-guard { background: #ffebee; color: #b71c1c; }
    .badge-general { background: #f5f5f5; color: #424242; }
    .pipeline-step {
        padding: 4px 0;
        font-size: 0.9em;
        border-left: 3px solid #1976d2;
        padding-left: 12px;
        margin: 4px 0;
    }
    .time-badge {
        display: inline-block;
        padding: 2px 8px;
        background: #e8eaf6;
        border-radius: 8px;
        font-size: 0.8em;
        color: #283593;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("🛡️ Fabric 365")
    st.caption("Enterprise Certification Readiness")

    st.divider()

    # Chat management
    if "chats" not in st.session_state:
        st.session_state.chats = {"Chat 1": {"messages": [], "context": {"employee_id": None, "team_id": None, "certification": None, "role": None}}}
        st.session_state.active_chat = "Chat 1"

    if st.button("➕ New Chat", use_container_width=True):
        chat_num = len(st.session_state.chats) + 1
        name = f"Chat {chat_num}"
        st.session_state.chats[name] = {"messages": [], "context": {"employee_id": None, "team_id": None, "certification": None, "role": None}}
        st.session_state.active_chat = name
        st.rerun()

    st.markdown("**Chats**")
    for chat_name in list(st.session_state.chats.keys()):
        is_active = chat_name == st.session_state.active_chat
        col_chat, col_del = st.columns([4, 1])
        with col_chat:
            label = f"**{chat_name}**" if is_active else chat_name
            if st.button(f"💬 {label}", key=f"chat_{chat_name}", use_container_width=True):
                st.session_state.active_chat = chat_name
                st.rerun()
        with col_del:
            if len(st.session_state.chats) > 1:
                if st.button("🗑️", key=f"del_{chat_name}"):
                    del st.session_state.chats[chat_name]
                    if st.session_state.active_chat == chat_name:
                        st.session_state.active_chat = list(st.session_state.chats.keys())[0]
                    st.rerun()

    st.divider()

    # System Status
    st.markdown("**System Status**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🟢 Foundry Model")
        st.markdown("🟢 AI Search")
    with col2:
        st.markdown("🟢 Learn API")
        st.markdown("🟢 Pipeline")

    st.divider()

    # Clear current chat button
    if st.button("🗑️ Clear Current Chat", use_container_width=True):
        st.session_state.chats[st.session_state.active_chat] = {"messages": [], "context": {"employee_id": None, "team_id": None, "certification": None, "role": None}}
        st.rerun()

    st.divider()
    st.caption("Built for Microsoft AI Skills Fest\nAgent League · Battle #2")


# ============================================================
# Agent Badge Helper
# ============================================================

AGENT_BADGES = {
    "learning_path": ("📚 Learning Path Curator", "badge-curator"),
    "study_plan": ("📅 Study Plan Generator", "badge-plan"),
    "engagement": ("⏰ Engagement Agent", "badge-engage"),
    "assessment": ("📝 Assessment Agent", "badge-assess"),
    "manager_insights": ("📊 Manager Insights", "badge-manager"),
    "general": ("🎯 Mission Control", "badge-general"),
    "chain": ("🔗 Multi-Agent Chain", "badge-curator"),
}


def render_agent_badge(agent_key: str, extra: str = ""):
    label, css_class = AGENT_BADGES.get(agent_key, ("🤖 Agent", "badge-general"))
    badge_html = f'<span class="agent-badge {css_class}">{label}</span>'
    if extra:
        badge_html += f' <span class="time-badge">{extra}</span>'
    st.markdown(badge_html, unsafe_allow_html=True)


# ============================================================
# Main Chat Interface
# ============================================================

st.title("🛡️ Fabric 365")
st.markdown("*Enterprise Certification Readiness — 8 Agents · 10 Reasoning Techniques · Governance Pipeline*")

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": {"messages": [], "context": {"employee_id": None, "team_id": None, "certification": None, "role": None}}}
    st.session_state.active_chat = "Chat 1"

# Point to active chat
active = st.session_state.chats[st.session_state.active_chat]
if "messages" not in st.session_state:
    st.session_state.messages = active["messages"]
if "context" not in st.session_state:
    st.session_state.context = active["context"]

# Sync active chat
st.session_state.messages = active["messages"]
st.session_state.context = active["context"]

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🛡️"):
        if message["role"] == "assistant" and "agent_key" in message:
            render_agent_badge(message["agent_key"], message.get("time_str", ""))
        st.markdown(message["content"])
        if "pipeline_steps" in message and message["pipeline_steps"]:
            with st.expander("🔍 Reasoning Pipeline", expanded=False):
                for step in message["pipeline_steps"]:
                    st.markdown(f'<div class="pipeline-step">{step}</div>', unsafe_allow_html=True)


# ============================================================
# Pipeline (adapted for Streamlit with live status)
# ============================================================

def run_streamlit_pipeline(user_message: str, status_container) -> dict:
    """Run the full pipeline with live status updates."""
    client = get_client()
    context = st.session_state.context
    audit = AuditTrail()
    audit.start(user_message)
    pipeline_steps = []
    agent_key = "general"

    # Pre-check greetings
    greeting_patterns = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                         "what can you do", "who are you", "thanks", "thank you", "bye"]
    if user_message.strip().lower().rstrip("!?.") in greeting_patterns or len(user_message.strip()) < 4:
        pipeline_steps.append("🎯 Greeting detected → direct response")
        return {
            "response": "Hello! I'm Fabric 365. I can help with:\n- **Certification paths** — \"What certs for a Cloud Engineer?\"\n- **Study plans** — \"Create a plan for EMP-034\"\n- **Practice questions** — \"Quiz me on AZ-400\"\n- **Engagement reminders** — \"When should EMP-056 study?\"\n- **Team insights** — \"How is TEAM-D doing?\"\n\nWhat would you like help with?",
            "agent_key": "general",
            "pipeline_steps": pipeline_steps,
        }

    # Step 1: Route
    status_container.markdown("🎯 **Mission Control** — classifying intent...")
    pipeline_steps.append("🎯 Mission Control: classifying intent...")
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

    if routing.get("reasoning"):
        pipeline_steps.append(f"💡 Reasoning: {routing['reasoning']}")

    # Handle general
    if agent_key == "general":
        direct = routing.get("direct_response", "I can help with certification paths, study plans, practice questions, reminders, and team insights. What would you like?")
        pipeline_steps.append("🎯 Direct response (no specialist needed)")
        return {"response": direct, "agent_key": "general", "pipeline_steps": pipeline_steps}

    # Handle low confidence
    if isinstance(confidence, (int, float)) and confidence < 0.6:
        pipeline_steps.append(f"⚠️ Low confidence ({confidence}) → asking for clarification")
        return {
            "response": "I'm not quite sure what you need. Could you clarify? I can help with:\n- Certification recommendations\n- Study plans\n- Practice questions\n- Reminders\n- Team progress",
            "agent_key": "general",
            "pipeline_steps": pipeline_steps,
        }

    # Step 2: Chain or single agent
    chain = None
    msg_lower = user_message.lower()
    if any(kw in msg_lower for kw in ["prepare", "full plan", "help me get ready", "end to end"]):
        chain = CHAIN_DEFINITIONS["full_preparation"]
    elif any(kw in msg_lower for kw in ["am i ready", "readiness check", "should i take the exam"]):
        chain = CHAIN_DEFINITIONS["readiness_check"]

    if chain:
        chain_labels = [AGENT_CONFIG[a]["label"] for a in chain]
        status_container.markdown(f"🔗 **Chain:** {' → '.join(chain_labels)}")
        pipeline_steps.append(f"🔗 Multi-Agent Chain: {' → '.join(chain_labels)}")
        agent_key = "chain"

        previous_output = ""
        final_parts = []
        for i, agent_key_in_chain in enumerate(chain):
            config = AGENT_CONFIG[agent_key_in_chain]
            status_container.markdown(f"⏳ [{i+1}/{len(chain)}] **{config['label']}** processing...")
            pipeline_steps.append(f"  [{i+1}/{len(chain)}] {config['label']} ✓")
            response = call_single_agent(client, agent_key_in_chain, user_message, context, audit, previous_output)
            previous_output = response
            final_parts.append(f"**{config['label']}:**\n\n{response}")

        agent_output = "\n\n---\n\n".join(final_parts)
    else:
        config = AGENT_CONFIG.get(agent_key, AGENT_CONFIG["learning_path"])
        status_container.markdown(f"⏳ **{config['label']}** processing...")
        pipeline_steps.append(f"🔄 Routed → {config['label']}")
        agent_output = call_single_agent(client, agent_key, user_message, context, audit)

    # Step 3: Governance
    status_container.markdown("🛡️ **Governance** — Policy Guard + Verifier...")
    pipeline_steps.append("🛡️ Policy Guard (5-layer) + Verifier...")
    effective_key = chain[0] if chain else agent_key
    blocked, final_output = run_governance(client, agent_output, effective_key, user_message, context, audit)

    if blocked:
        pipeline_steps.append("❌ BLOCKED by Policy Guard")
        return {
            "response": "⚠️ Response blocked by Policy Guard due to policy violations.",
            "agent_key": "guard",
            "pipeline_steps": pipeline_steps,
        }

    pipeline_steps.append("✅ Governance passed — APPROVED")

    # Format
    formatted = format_response(final_output)
    trail = audit.finalize()
    pipeline_steps.append(f"📋 Audit: `{trail['pipeline_id']}` ({trail['total_time_seconds']}s)")

    return {
        "response": formatted,
        "agent_key": agent_key if not chain else "chain",
        "pipeline_steps": pipeline_steps,
    }


# ============================================================
# Chat Input
# ============================================================

# Show starter prompts if chat is empty
if not st.session_state.messages:
    st.markdown("**Try one of these to get started:**")
    cols = st.columns(3)
    starter_prompts = [
        "What certs should a Cloud Engineer get?",
        "Create a study plan for EMP-034",
        "Help me prepare for AZ-204",
        "How is TEAM-D performing?",
        "Give me practice questions for AZ-400",
        "When should EMP-056 study this week?",
    ]
    for i, prompt_text in enumerate(starter_prompts):
        with cols[i % 3]:
            if st.button(prompt_text, key=f"start_{i}", use_container_width=True):
                st.session_state["next_input"] = prompt_text
                st.rerun()
    st.markdown("---")

prompt = st.chat_input("Ask Fabric 365 anything about certifications...")

if "next_input" in st.session_state:
    prompt = st.session_state.pop("next_input")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate response with live status
    with st.chat_message("assistant", avatar="🛡️"):
        status_placeholder = st.empty()
        start = time.time()

        result = run_streamlit_pipeline(prompt, status_placeholder)

        elapsed = round(time.time() - start, 1)
        time_str = f"{elapsed}s"

        # Clear the status and show final response
        status_placeholder.empty()

        # Show agent badge
        render_agent_badge(result["agent_key"], time_str)

        # Show response
        st.markdown(result["response"])

        # Show pipeline steps
        if result.get("pipeline_steps"):
            with st.expander("🔍 Reasoning Pipeline", expanded=False):
                for step in result["pipeline_steps"]:
                    st.markdown(f'<div class="pipeline-step">{step}</div>', unsafe_allow_html=True)

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "agent_key": result["agent_key"],
        "time_str": time_str,
        "pipeline_steps": result.get("pipeline_steps", []),
    })
