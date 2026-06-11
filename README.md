# SkillSentinel — Multi-Agent Enterprise Certification Readiness System

> **All data in this repository is synthetic. No real employee names, company data, or PII is included.**

A multi-agent system built for the Microsoft Foundry Reasoning Agents Challenge. It helps organizations manage internal team certification programs through intelligent routing, capacity-aware planning, grounded knowledge retrieval, and multi-step Chain-of-Thought reasoning.

---

## Quick Start

```powershell
# 1. Clone and enter the project
git clone https://github.com/MinThu63/reasoning-agents-challenge.git
cd reasoning-agents-challenge

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 3. Install dependencies (just 2 packages)
pip install -r requirements.txt

# 4. Create .env file with your Azure credentials
# AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
# AZURE_AI_MODEL_DEPLOYMENT=gpt-oss-120b
# AZURE_AI_API_KEY=your-key

# 5. Run the interactive demo
python main.py

# 6. Run the evaluation suite
python test_scenarios.py
```

---

## Architecture

```
USER REQUEST
     ↓
┌─────────────────────────────────────┐
│  🎯 Mission Control (Orchestrator)  │
│  • Classifies intent via ARM-CoT    │
│  • Detects complex requests         │
│  • Routes OR chains agents          │
└────────────┬────────────────────────┘
             ↓
┌─ SINGLE AGENT ──────────────────────────────────────────────┐
│                                                              │
│  📚 Learning Path Curator      (Foundry IQ — ADORE RAG)     │
│  📅 Study Plan Generator       (Fabric IQ — CoT Planning)   │
│  ⏰ Engagement Agent           (Work IQ — CoT Scheduling)   │
│  📝 Assessment Agent           (Foundry IQ — Claim-Evidence) │
│  📊 Manager Insights           (Fabric IQ + Work IQ)        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
             ↓
┌─ OR MULTI-AGENT CHAIN (for complex requests) ───────────────┐
│  Curator → Study Plan → Engagement (chained sequentially)    │
│  Assessment → Study Plan (readiness check chain)             │
└──────────────────────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  🔒 Human Approval Gate            │
│  (Study plan modifications only)    │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────────┐
│  🛡️ Policy Guard         (5-Layer Safety Check)             │
│  ✅ Verifier              (Self-Consistency Quality Gate)    │
└────────────┬────────────────────────────────────────────────┘
             ↓
        📋 Audit Trail (logged to audit_logs/)
             ↓
        Final Response → User
```

---

## How It Works

1. User types a message (e.g., "Help me prepare for AZ-204")
2. **Mission Control** classifies intent and detects complexity:
   - Simple request → routes to one agent
   - Complex request → chains multiple agents sequentially
3. Each agent loads its IQ layer data and reasons step-by-step (CoT)
4. **Human Approval Gate** pauses for confirmation on study plans
5. **Policy Guard** runs 5-layer compliance check
6. **Verifier** validates citation coverage and consistency
7. **Audit Trail** logs the full pipeline to `audit_logs/`
8. Formatted response returned to user

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Chaining** | Complex requests trigger sequential agent calls (e.g., Curator → Study Plan → Engagement) with output passed between agents |
| **Human Approval Gates** | Study plan generation pauses for user confirmation before proceeding |
| **Permission-Aware Retrieval** | Knowledge base content filtered by role — simulates Foundry IQ RBAC |
| **Audit Trail** | Every pipeline run logged to JSON with timestamps, agent calls, governance results |
| **Policy Guard** | 5-layer check: PII, credentials, grounding compliance, prompt injection, scope |
| **Verifier** | Citation coverage (≥85%), reasoning completeness, internal consistency |
| **Evaluation Framework** | 8 automated test scenarios with keyword validation and scoring |
| **Chain-of-Thought** | All agents reason step-by-step (STEP 1→4) before answering |
| **Source-Grounding** | Zero unsourced claims — every fact cites `[source: filename, section: ...]` |
| **Anti-Extrapolation** | Agents flag assumptions explicitly instead of silently filling gaps |

---

## Agents — Responsibilities

| # | Agent | IQ Layer | Role |
|---|-------|----------|------|
| 1 | 🎯 Mission Control | — | Routes requests, detects chains, handles greetings |
| 2 | 📚 Learning Path Curator | Foundry IQ | Maps certs to roles, prerequisite chains, grounded resources |
| 3 | 📅 Study Plan Generator | Fabric IQ | Week-by-week plans, capacity risk, fallback paths |
| 4 | ⏰ Engagement Agent | Work IQ | Personalized reminders, safe windows, tone adaptation |
| 5 | 📝 Assessment Agent | Foundry IQ | Grounded practice questions, readiness scoring |
| 6 | 📊 Manager Insights | Fabric IQ + Work IQ | Team aggregates, health ratings, privacy-preserving |
| 7 | 🛡️ Policy Guard | — | PII/credential/injection/scope/grounding checks |
| 8 | ✅ Verifier | — | Citation coverage, completeness, consistency audit |

---

## IQ Layer Integration

| Layer | What It Provides | Data Source |
|-------|------------------|-------------|
| **Foundry IQ** | Grounded knowledge retrieval (company docs) | `docs/engineering_certification_guide.md` |
| **Fabric IQ** | Semantic business model (roles, certs, rules) | `data/semantic_model.json` |
| **Work IQ** | Employee work patterns and calendar signals | `data/work_activity_signals.json` |

---

## Universal Constraints (House Rules)

Every agent enforces these 4 rules (defined in `agents/base.py`):

1. **SOURCE-GROUNDING MANDATE** — Every factual claim cites `[source: <file>, section: <section>]`
2. **ANTI-EXTRAPOLATION GUARD** — Unknown info flagged as `ASSUMPTION FLAG`, never silently filled
3. **CHAIN-OF-THOUGHT MANDATE** — STEP 1→4 reasoning before every answer
4. **OUTPUT FORMAT LOCK** — Structured JSON internally, converted to natural language for user

---

## Project Structure

```
├── main.py                          ← Entry point (interactive demo + full pipeline)
├── test_scenarios.py                ← Evaluation framework (8 test cases)
├── agents/
│   ├── __init__.py
│   ├── base.py                      ← Universal constraints (house rules)
│   ├── mission_control.py           ← Agent 1: Orchestrator + chaining
│   ├── learning_path_curator.py     ← Agent 2: Foundry IQ
│   ├── study_plan_generator.py      ← Agent 3: Fabric IQ
│   ├── engagement_agent.py          ← Agent 4: Work IQ
│   ├── assessment_agent.py          ← Agent 5: Foundry IQ
│   ├── manager_insights_agent.py    ← Agent 6: Fabric IQ + Work IQ
│   ├── policy_guard.py              ← Agent 7: Safety
│   └── verifier.py                  ← Agent 8: Quality
├── data/
│   ├── semantic_model.json          ← Fabric IQ (roles, certs, rules, templates)
│   ├── work_activity_signals.json   ← Work IQ (18 employees)
│   └── learner_performance.json     ← Learner outcomes (18 records)
├── docs/
│   ├── engineering_certification_guide.md   ← Foundry IQ knowledge base
│   ├── corporate_learning_policy.md
│   ├── quarterly_learning_report.md
│   ├── challengeDetails.md          ← Challenge requirements
│   └── newPlan.md                   ← Architecture design document
├── audit_logs/                      ← Auto-generated pipeline audit trails
├── requirements.txt                 ← python-dotenv, openai
├── .env                             ← Azure credentials (not committed)
└── .gitignore
```

---

## Usage Examples

### Interactive Demo
```
👤 You: What certifications should a Cloud Engineer get?
  🔄 Mission Control → 📚 Learning Path Curator
  🛡️ Running governance checks... ✓
  ✅ Verifier: APPROVED
  📋 Audit: run-1718100000 (8.2s)

🤖 SkillSentinel:
As a Cloud Engineer, here's your recommended path...
- Start with AZ-204 (Azure Developer Associate) — 25 hours
- Then AZ-305 (Solutions Architect Expert) — 30 hours, requires AZ-104
...
```

### Multi-Agent Chaining
```
👤 You: Help me prepare for AZ-204
  🔗 Mission Control → Chain: 📚 Learning Path Curator → 📅 Study Plan Generator → ⏰ Engagement Agent
    [1/3] 📚 Learning Path Curator... ✓
    [2/3] 📅 Study Plan Generator... ✓
    [3/3] ⏰ Engagement Agent... ✓

  🔒 Human Approval Gate: Study plan generated.
     Approve this plan? [Y/n]: Y
  🛡️ Running governance checks... ✓
  📋 Audit: run-1718100100 (24.1s)
```

### Evaluation Suite
```powershell
python test_scenarios.py

  [TC-001] Learning Path — Cloud Engineer... ✅ PASS (7.2s) [4/4]
  [TC-002] Study Plan — At-Risk Employee... ✅ PASS (9.1s) [3/3]
  [TC-005] Manager Insights — Team D... ✅ PASS (8.4s) [5/5]
  ...

  RESULTS: 7/8 scenarios passed
  SCORE: 28/32 (87.5%)
  TOTAL TIME: 62.3s (avg 7.8s per scenario)
```

---

## Reasoning Techniques — Summary

| Technique | Status | Research | Agents Using It |
|-----------|--------|----------|-----------------|
| Retrieval-Augmented Generation (ADORE) | ✅ | Lewis et al. (2020), arXiv:2601.18267 | Curator, Assessment |
| Chain-of-Thought (CoT) | ✅ | Wei et al. (2022) | All 8 agents |
| Deductive Reasoning | ✅ | Classical AI | Mission Control (rules→routing), Policy Guard (rules→block/pass) |
| Abductive Reasoning | ✅ | Peirce (1903), Diagnostic AI | Manager Insights (hypothesizing causes from patterns) |
| Analogical Reasoning | ✅ | Gentner (1983) | Study Plan Generator (comparing to similar learner profiles) |
| Nonmonotonic Reasoning | ✅ | McCarthy (1980) | Study Plan, Engagement (revising conclusions on new info) |
| Prompt Engineering & In-Context Constraints | ✅ | Microsoft Foundry Best Practices | All 8 agents |
| Source-Grounding Mandate | ✅ | IMDA Framework | All 8 agents + Policy Guard enforcement |
| Anti-Extrapolation & Assumption Bias Guard | ✅ | IMDA Framework | All 8 agents + Verifier audit |
| Few-Shot Constraint Demonstrations | ✅ | Brown et al. (2020) | Curator, Study Plan, Engagement, Assessment, Manager, Mission Control |
| Self-Consistency CoT | ✅ | Wang et al. (2022) | Verifier |
| ARM-Pattern Routing | ✅ | ICLR 2026 | Mission Control |
| Layered-CoT | ✅ | arXiv:2501.18645 | Policy Guard (5-layer) |
| Geospatial Foundations | ❌ N/A | — | Not applicable to certification domain |

---

## Reasoning Techniques — Detailed Implementation

### 1. Retrieval-Augmented Generation (RAG) — ADORE Pattern
**Research:** Lewis et al. (2020); ADORE (arXiv:2601.18267)

**What it is:** Instead of one-shot retrieval, agents use an iterative retrieval loop that continues until evidence coverage thresholds are met. Questions and recommendations must map to specific evidence nodes in a Claim-Evidence Graph.

**How we implement it:**
- Learning Path Curator uses a 3-round retrieval protocol: (1) identify skill domains, (2) find resources per domain, (3) flag gaps with `NO_APPROVED_SOURCE`
- Assessment Agent maps every question to a specific source passage — questions without citation are discarded
- `retrieve_with_permissions()` in `main.py` simulates Foundry IQ permission-aware retrieval, filtering content by role

**Intended impact:** Eliminates hallucinated content. Every answer is traceable to an approved source document. Judges can verify grounding directly by checking citations.

---

### 2. Chain-of-Thought (CoT) — All Agents
**Research:** Wei et al. (2022), Google Research — "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"

**What it is:** Providing intermediate reasoning steps in prompts dramatically improves LLM accuracy on multi-step tasks. Emergent above ~100B parameters.

**How we implement it:**
- All 8 agents have explicit STEP 1→4 reasoning scaffolding in their instructions
- Mission Control uses ARM-pattern CoT routing (ICLR 2026) — each routing decision is a reasoned step, not a single token prediction
- Verifier uses Self-Consistency CoT (Wang et al. 2022) — validates outputs against multiple quality dimensions
- Universal constraint #3 enforces CoT format: `STEP 1 → STEP 2 → STEP 3 → STEP 4 → FINAL ANSWER`

**Intended impact:** Dramatically improves multi-step reasoning accuracy. Makes agent decisions interpretable and auditable. Directly satisfies the hackathon rubric "Reasoning & Multi-Step Thinking" (25% of score).

---

### 3. Prompt Engineering & In-Context Constraints
**Research:** Microsoft Foundry Prompt Engineering Best Practices

**What it is:** Structured prompt design with system role anchoring, hard output format locks, negative constraints, and instruction repetition.

**How we implement it:**
- `agents/base.py` defines a universal system role anchor inherited by all agents
- Hard OUTPUT FORMAT LOCK (JSON only) prevents format drift
- Negative constraints explicitly state what NOT to do (e.g., "NEVER generate unsourced factual claims")
- Each agent has both correct and incorrect few-shot examples to anchor behavior

**Intended impact:** Reduces format drift, enforces predictable structured outputs, aligns with Foundry best practices for reliable tool-calling.

---

### 4. Source-Grounding Mandate
**Research:** Foundry IQ grounding principles; IMDA Agentic AI Governance Framework

**What it is:** Every factual claim in agent output must cite its source in a specific format. Uncited claims trigger discard or assumption flags. Policy Guard Layer 3 enforces ≥85% citation coverage.

**How we implement it:**
- Universal constraint #1: `[source: <filename>, section: <section>]` format required
- Assessment Agent discards any question without a direct source mapping
- Policy Guard Layer 3 (Grounding Compliance) checks citation ratio
- Verifier Layer 1 calculates `citation_coverage = cited_claims / total_claims` and rejects if <0.85
- Context builders prepend `[source: ...]` labels to all injected data

**Intended impact:** Core anti-hallucination control. Makes the system IMDA-compliant on transparency. Enables the Verifier to audit every claim has a source.

---

### 5. Anti-Extrapolation & Assumption Bias Guard
**Research:** IMDA Agentic AI Governance Framework

**What it is:** Agents must explicitly flag when operating beyond grounded evidence rather than silently filling gaps with model knowledge.

**How we implement it:**
- Universal constraint #2: If context is insufficient, agents must state `"ASSUMPTION FLAG: The following is inferred, not retrieved: <statement>"`
- Verifier Layer 4 counts all ASSUMPTION FLAGs — more than 3 triggers ESCALATE status
- Escalated outputs require human review (not auto-released to user)
- Learning Path Curator flags skill domains with no approved source as `NO_APPROVED_SOURCE`

**Intended impact:** Prevents silent knowledge gap filling — the most dangerous failure mode in enterprise AI. Forces the system to surface uncertainty rather than hide it.

---

### 6. Few-Shot Constraint Demonstrations
**Research:** Brown et al. (2020); prompt anchoring best practices

**What it is:** Including both correct and incorrect example pairs in agent prompts anchors output format and quality without fine-tuning.

**How we implement it:**
- Every specialized agent (Curator, Study Plan, Engagement, Assessment, Manager Insights) contains:
  - A **CORRECT OUTPUT** example showing exact JSON format, citations, and reasoning trace
  - An **INCORRECT OUTPUT** example showing what NOT to do and WHY it's wrong
- Mission Control has routing exemplars showing correct classification for different message types

**Intended impact:** Anchors output format and quality to a known-good example. Reduces format errors without fine-tuning. Particularly effective on structured JSON output tasks. Helps the model understand boundaries between acceptable and unacceptable responses.

---

### 7. Abductive Reasoning (Hypothesis Generation)
**Research:** Peirce (1903); standard in diagnostic AI systems

**What it is:** Starting with observed patterns (effects) and reasoning backward to the most likely cause. Unlike deduction (which guarantees truth), abduction produces hypotheses that explain the data.

**How we implement it:**
- Manager Insights Agent (Step 4) observes patterns like "TEAM-D has 57% pass rate with 22 avg meeting hours"
- Instead of just reporting numbers, it explicitly hypothesizes: "Most likely cause: insufficient study time due to meeting overload"
- Hypotheses are labeled as inferred, not confirmed: prevents presenting correlation as causation
- Recommendations target the hypothesized cause (e.g., "conduct meeting audit") rather than generic advice

**Intended impact:** Transforms the Manager Insights agent from a dashboard (just numbers) into an analytical advisor (numbers + explanations + actionable hypotheses). Judges see reasoning, not just data retrieval.

---

### 8. Analogical Reasoning (Pattern Transfer)
**Research:** Gentner (1983) — Structure-Mapping Theory

**What it is:** Solving problems by finding similar past cases and transferring knowledge. "Employee X has a similar profile to Employee Y who succeeded — here's what worked."

**How we implement it:**
- Study Plan Generator (Step 4) searches `learner_performance.json` for employees with similar:
  - Role + certification target
  - Meeting load range
  - Starting practice score
- If a match is found: "Based on similar learner profiles, employees with ~21 meeting hours who passed AZ-400 studied for 8 weeks with evening sessions"
- If a matching employee failed: identifies what was different and adjusts the plan to avoid the same outcome

**Intended impact:** Adds data-driven personalization beyond template-following. Shows judges the system learns from historical patterns, not just applies static rules.

---

### 9. Nonmonotonic Reasoning (Belief Revision)
**Research:** McCarthy (1980); used in adaptive AI systems

**What it is:** The ability to revise conclusions when new information contradicts prior assumptions. Unlike monotonic logic where conclusions are permanent, nonmonotonic systems update their beliefs.

**How we implement it:**
- Study Plan Generator (Step 5): If user says "I actually only have 2 hours per week" after a plan was suggested assuming 4 hours, the agent explicitly states: "Revising standard template based on new constraint" and produces an adjusted plan
- Engagement Agent (Step 4): If progress data shows the current reminder strategy isn't working (scores declining despite reminders), the agent pivots: "Revising engagement approach because current strategy is not producing results"
- Universal Constraint #5 instructs all agents to label when they are applying nonmonotonic reasoning

**Intended impact:** Shows judges the system is adaptive, not rigid. Real enterprise systems must handle changing requirements — this demonstrates that capability explicitly.

---

### Design Note: Why We Use Explicit CoT (Not Internal Reasoning)

The OpenAI Reasoning Best Practices document notes that o-series models (o1, o3, o4-mini) reason internally and do NOT benefit from "think step by step" prompts. However, our system uses `gpt-oss-120b`, which is a GPT-class model that DOES benefit from explicit Chain-of-Thought scaffolding (Wei et al. 2022). This is a deliberate architectural choice:

- GPT models + explicit CoT → improved accuracy on multi-step tasks
- The visible reasoning trace provides auditability (judges can see HOW the agent decided)
- Aligns with IMDA governance requirements for explainable AI

If migrated to o-series models in production, the CoT scaffolding in prompts would be removed and replaced with simple, direct instructions per OpenAI's guidance.

---

## Synthetic Data

- **Employee IDs:** EMP-001 through EMP-105 (18 records)
- **Learner IDs:** L-1001 through L-1105
- **Teams:** TEAM-A through TEAM-E (5 engineering teams)
- **Certifications:** AZ-104, AZ-204, AZ-305, AZ-400, AZ-500, DP-100, DP-203, DP-300, SC-200
- **Roles:** Cloud Engineer, DevOps Engineer, Data Engineer, Security Engineer

---

## For Collaborators

### How to add a new agent

1. Create `agents/your_agent.py` with an `INSTRUCTIONS` string
2. Add a context builder function in `main.py`
3. Add the agent to `AGENT_CONFIG` dict in `main.py`
4. Optionally add it to `CHAIN_DEFINITIONS` if it should participate in chains

### How to add a test scenario

Add an entry to `TEST_SCENARIOS` in `test_scenarios.py`:
```python
{
    "id": "TC-009",
    "name": "Your Test Name",
    "input": "User message to test",
    "expected_agent": "agent_key",
    "expected_keywords": ["word1", "word2"],
    "expected_no_keywords": ["forbidden_word"],
}
```

### How the pipeline works (for debugging)

```
main.py:run_pipeline()
  ├── call_llm(Mission Control) → routing JSON
  ├── detect chain or single agent
  ├── call_single_agent() [× N if chaining]
  │     └── context_builder → build_prompt → call_llm
  ├── Human Approval Gate (if study_plan involved)
  ├── run_governance()
  │     ├── call_llm(Policy Guard) → CLEARED/BLOCKED
  │     └── call_llm(Verifier) → APPROVED/REVISE/ESCALATE
  ├── format_response() (JSON → readable, no LLM call)
  └── AuditTrail.finalize() → saves to audit_logs/
```

### Environment variables (.env)

```
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT=gpt-oss-120b
AZURE_AI_API_KEY=your-api-key
```

---

## Challenge Alignment

| Criterion | Score Weight | How We Address It |
|-----------|-------------|-------------------|
| Accuracy & Relevance | 25% | Source-grounding mandate, Foundry IQ retrieval, Fabric IQ business rules |
| Reasoning & Multi-step Thinking | 25% | CoT in all agents, agent chaining, ARM routing, self-consistency verification |
| Creativity & Originality | 15% | 8-agent pipeline with governance layer, ADORE RAG, research-backed design |
| User Experience & Presentation | 15% | Natural language responses, clear pipeline feedback, audit command |
| Reliability & Safety | 20% | Policy Guard (5-layer), Verifier, human approval gates, anti-extrapolation guards |

---

## Known Limitations

- **Knowledge base connection:** Foundry IQ knowledge base has auth issues due to Azure for Students subscription region restrictions. Grounding is achieved through local document loading in agent prompts. In production with a standard subscription, Foundry IQ would provide cited retrieval directly.
- **Latency:** Each request makes 3-4 LLM calls (routing + agent + guard + verifier). Complex chains add more. Average response time is 7-10 seconds per request.
- **Model:** Uses `gpt-oss-120b` which may not always produce perfectly structured JSON. A gpt-4o deployment would improve structured output reliability.

---

## License

MIT
