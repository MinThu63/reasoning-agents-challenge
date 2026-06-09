# SkillSentinel — Multi-Agent Enterprise Certification Readiness System

> **All data in this repository is synthetic. No real employee names, company data, or PII is included.**

A multi-agent system built for the Microsoft Foundry Reasoning Agents Challenge. It helps organizations manage internal team certification programs through intelligent routing, capacity-aware planning, grounded knowledge retrieval, and multi-step Chain-of-Thought reasoning.

---

## Architecture

```
User Request
     ↓
┌─────────────────────────────────┐
│  🎯 Mission Control (Router)    │  ← ARM-pattern CoT routing
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  📚 Learning Path Curator      (Foundry IQ — ADORE RAG)    │
│  📅 Study Plan Generator       (Fabric IQ — CoT Planning)  │
│  ⏰ Engagement Agent           (Work IQ — CoT Scheduling)  │
│  📝 Assessment Agent           (Foundry IQ — Claim-Evidence)│
│  📊 Manager Insights Agent     (Fabric IQ + Work IQ)       │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  🛡️ Policy Guard         (5-Layer Safety Check)             │
│  ✅ Verifier              (Self-Consistency Quality Gate)    │
└─────────────────────────────────────────────────────────────┘
              ↓
        Final Response (Structured JSON)
```

---

## How It Works

1. User types a message (e.g., "Create a study plan for EMP-034")
2. **Mission Control** classifies intent using Chain-of-Thought routing and dispatches to the correct agent
3. The specialized agent loads relevant IQ layer data and reasons step-by-step
4. **Policy Guard** runs a 5-layer compliance check (PII, credentials, grounding, injection, scope)
5. **Verifier** validates citation coverage, reasoning completeness, and internal consistency
6. The structured JSON response is returned to the user

---

## Reasoning Techniques Applied

| Technique | Source | Application |
|-----------|--------|-------------|
| Chain-of-Thought (CoT) | Wei et al. (2022) | All 8 agents use explicit STEP 1→4 reasoning |
| RAG (ADORE Pattern) | arXiv:2601.18267 | Iterative retrieval in Curator + Assessment |
| Self-Consistency CoT | Wang et al. (2022) | Verifier cross-checks outputs |
| ARM Routing | ICLR 2026 | Mission Control routing as CoT blocks |
| Layered-CoT | arXiv:2501.18645 | Policy Guard 5-layer check |
| Source-Grounding Mandate | — | Zero unsourced claims allowed |
| Anti-Extrapolation Guard | IMDA Framework | Explicit assumption flagging |

---

## IQ Layer Integration

| Layer | Purpose | Data Source |
|-------|---------|-------------|
| **Foundry IQ** | Grounded knowledge retrieval | `docs/engineering_certification_guide.md` |
| **Fabric IQ** | Semantic business model | `data/semantic_model.json` |
| **Work IQ** | Employee work patterns | `data/work_activity_signals.json` |

---

## Universal Constraints (House Rules)

Every agent enforces these 4 rules:

1. **SOURCE-GROUNDING MANDATE** — Every factual claim must cite `[source: <file>, section: <section>]`
2. **ANTI-EXTRAPOLATION GUARD** — Unknown info flagged as `ASSUMPTION FLAG`, never silently filled
3. **CHAIN-OF-THOUGHT MANDATE** — Every response shows STEP 1→4 reasoning before the answer
4. **OUTPUT FORMAT LOCK** — All outputs are structured JSON with a `reasoning_trace` field

---

## Agents — Responsibilities

### 1. Mission Control (Orchestrator)
- Classifies user intent via ARM-pattern CoT
- Extracts context (employee ID, team, certification)
- Routes to the correct specialized agent
- Never answers directly — strictly routing

### 2. Learning Path Curator (Foundry IQ)
- Maps certifications to roles with prerequisite chains
- Uses ADORE iterative retrieval pattern
- Cites `engineering_certification_guide.md` for all recommendations
- Flags skill domains with no approved source

### 3. Study Plan Generator (Fabric IQ)
- Creates week-by-week study plans with target scores
- Accounts for meeting load, focus hours, calendar fragmentation
- Flags CAPACITY_RISK when meetings >20 hrs/week
- Includes fallback paths and buffer weeks

### 4. Engagement Agent (Work IQ)
- Suggests study-safe windows based on work patterns
- Adapts tone to workload (encouraging/empathetic)
- Never schedules during meetings or outside 08:00-21:00
- Defines escalation triggers for manager involvement

### 5. Assessment Agent (Foundry IQ)
- Generates scenario-based questions grounded in certification guide
- Zero-tolerance: discards any question without source citation
- Evaluates readiness: READY / BORDERLINE / NOT_READY
- Identifies weak domains for targeted study

### 6. Manager Insights Agent (Fabric IQ + Work IQ)
- Aggregates team metrics without exposing individual data
- Assigns health rating: GREEN / YELLOW / RED
- Identifies systemic patterns (high meetings → low pass rates)
- Provides actionable recommendations

### 7. Policy Guard (Safety Layer)
- 5-layer check: PII, credentials, grounding, injection, scope
- Blocks responses that violate any hard constraint
- Flags grounding gaps for Verifier review

### 8. Verifier (Quality Gate)
- Validates citation coverage (≥85% threshold)
- Checks reasoning completeness and internal consistency
- Audits assumption flags (>3 = escalate)
- Final APPROVED / REVISE / ESCALATE verdict

---

## Project Structure

```
├── main.py                          ← Entry point (run this)
├── agents/
│   ├── __init__.py
│   ├── base.py                      ← Universal constraints (house rules)
│   ├── mission_control.py           ← Agent 1: Orchestrator
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
│   ├── engineering_certification_guide.md   ← Foundry IQ knowledge
│   ├── corporate_learning_policy.md
│   └── quarterly_learning_report.md
├── requirements.txt
├── .env                             ← Azure credentials (not committed)
└── .gitignore
```

---

## Setup

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env
# AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
# AZURE_AI_MODEL_DEPLOYMENT=gpt-oss-120b
# AZURE_AI_API_KEY=your-key

# 4. Run
python main.py
```

---

## Usage

```
👤 You: What certifications should a Cloud Engineer get?
  🔄 Mission Control → 📚 Learning Path Curator
  ✅ Verifier: APPROVED

🤖 SkillSentinel:
{
  "certification": "AZ-204",
  "role": "Cloud Engineer",
  "prerequisite_path": [],
  "skill_domains": [...],
  "reasoning_trace": "STEP 1: User asked for cert recommendations..."
}

──────────────────────────────────────────────────────

👤 You: Create a study plan for EMP-034
  🔄 Mission Control → 📅 Study Plan Generator
  ⚠️ Verifier: REVISE — capacity risk not addressed
  ✅ Verifier: APPROVED

👤 You: How is TEAM-D doing?
  🔄 Mission Control → 📊 Manager Insights
  ✅ Verifier: APPROVED
```

---

## Synthetic Data

- **Employee IDs:** EMP-001 through EMP-105 (18 records)
- **Learner IDs:** L-1001 through L-1105
- **Teams:** TEAM-A through TEAM-E (5 engineering teams)
- **Certifications:** AZ-104, AZ-204, AZ-305, AZ-400, AZ-500, DP-100, DP-203, DP-300, SC-200
- **Roles:** Cloud Engineer, DevOps Engineer, Data Engineer, Security Engineer

---

## Challenge Requirements

- ✅ Multi-agent system (8 agents) with clear role specialization
- ✅ Microsoft Foundry model inference (gpt-oss-120b via API)
- ✅ Reasoning and multi-step decision-making (Chain-of-Thought in every agent)
- ✅ All three Microsoft IQ layers (Foundry IQ, Fabric IQ, Work IQ)
- ✅ Synthetic data only — no PII
- ✅ Demoable with clear agent interactions
- ✅ Safety controls (Policy Guard) and quality validation (Verifier)
- ✅ Source-grounding with citations and anti-hallucination guards
- ✅ Research-backed reasoning patterns (Wei et al., Wang et al., ADORE, ARM)

---

## Research References

1. Wei et al. (2022) — Chain-of-Thought Prompting Elicits Reasoning in LLMs
2. Wang et al. (2022) — Self-Consistency Improves CoT Reasoning
3. ADORE (2026) — Orchestrating Specialized Agents for Trustworthy Enterprise RAG (arXiv:2601.18267)
4. ARM (ICLR 2026) — Agentic Reasoning Modules
5. Sanwal (2025) — Layered Chain-of-Thought (arXiv:2501.18645)
6. IMDA — Agentic AI Governance Framework

---

## License

MIT
