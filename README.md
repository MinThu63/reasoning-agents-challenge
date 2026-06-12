# SkillSentinel — Multi-Agent Enterprise Certification Readiness System

> **All data in this repository is synthetic. No real employee names, company data, or PII is included.**

A governance-first, research-grounded multi-agent system built for the **Microsoft Foundry Reasoning Agents Challenge** (AI Skills Fest — Agent League, Battle #2). SkillSentinel helps organizations manage internal team certification programs through intelligent routing, capacity-aware planning, grounded knowledge retrieval, and multi-step Chain-of-Thought reasoning — with a 5-layer safety gate and self-consistency verification on every response.

---

## What Makes SkillSentinel Different

Most multi-agent systems in this challenge will implement 3-5 agents that call an LLM and return answers. SkillSentinel goes further:

1. **Governance-first pipeline** — Every response passes through a Policy Guard (5-layer safety check) AND a Verifier (quality gate) before reaching the user. Responses that fail citation coverage (≥85%) are automatically revised via a closed-loop REVISE mechanism.

2. **10 research-backed reasoning techniques** — Not just Chain-of-Thought. We implement ADORE RAG (iterative retrieval), abductive reasoning (hypothesis generation), analogical reasoning (pattern transfer from similar learners), nonmonotonic reasoning (belief revision on new data), and self-consistency verification — each with academic citations.

3. **Live external API integration** — Microsoft Learn Search API returns real-time documentation. Azure AI Search queries the Foundry IQ knowledge base. These are not simulations — they're live HTTP calls returning real data.

4. **Adaptive quality thresholds** — The Verifier doesn't apply a blanket 85% standard. Assessment outputs require 90% citation coverage. Engagement reminders only need 70%. This prevents over-blocking on low-risk content while maintaining rigor on high-stakes outputs.

5. **Routing confidence scoring** — Mission Control doesn't silently guess. When confidence is below 0.6, it asks for clarification instead of misrouting to the wrong agent.

6. **Red-team validated** — The evaluation suite includes adversarial test scenarios: prompt injection attempts, PII extraction, brain dump requests, scope bypass, and credential extraction. We test failure modes, not just happy paths.

7. **Full audit trail** — Every pipeline run produces a JSON audit log with timestamps, agent calls, governance decisions, and timing. This satisfies IMDA continuous monitoring requirements and gives judges a verification tool.

8. **Production deployment-ready** — Dockerfile, azure.yaml, and agent.manifest.yaml are included. The system runs in both interactive terminal mode (`python main.py`) and HTTP server mode (`python main.py --serve` on port 8088) for Foundry Hosted Agent deployment.

---

## Submission Requirements — How We Meet Each One

| Requirement | How SkillSentinel Addresses It | Evidence |
|---|---|---|
| **Multi-agent system aligned to challenge scenario** | 8 specialized agents covering the full certification lifecycle: path curation, study planning, engagement, assessment, team analytics, safety, and quality verification | `agents/` directory — 8 agent files |
| **Use Microsoft Foundry (UI or SDK)** | Model inference via Microsoft Foundry endpoint (`gpt-oss-120b`). Azure AI Search (Foundry IQ) for knowledge base retrieval. Deployment files for Foundry Agent Service. | `.env` → `AZURE_AI_PROJECT_ENDPOINT`, `agents/tools.py` → live API calls |
| **Demonstrate reasoning and multi-step decision-making** | 10 reasoning techniques implemented (CoT, ADORE RAG, abductive, analogical, nonmonotonic, deductive, self-consistency, ARM routing, layered-CoT, few-shot). Multi-agent chaining for complex requests. | `agents/base.py` → universal constraints, each agent file → STEP 1→4 scaffolding |
| **Integrate external tools, APIs, and/or MCP** | Microsoft Learn Search API (live, public). Azure AI Search API (live, authenticated). Both return real data injected into agent context. | `agents/tools.py` → `search_microsoft_learn()`, `query_knowledge_base()` |
| **Integrate at least one Microsoft IQ layer** | All three IQ layers: Foundry IQ (Azure AI Search + docs), Fabric IQ (semantic_model.json), Work IQ (work_activity_signals.json) | Context builders in `main.py`, data files in `data/` |
| **Use synthetic data and documents only** | All employee IDs, team names, learner records, and documents are clearly synthetic. README states this explicitly. | `data/` directory, docs, disclaimer at top |
| **Be demoable** | `python main.py` starts interactive demo. Pipeline status shows in real-time. Audit trail viewable via `audit` command. | `main.py` → `main()` function |
| **Clear documentation** | This README: architecture diagrams, per-agent specs, IQ layer details, reasoning technique explanations, deployment docs | This file |

**Highly Valued Extras:**

| Extra | How We Address It |
|---|---|
| Evaluations & telemetry | `test_scenarios.py` — 13 automated test cases (8 functional + 5 red-team adversarial) with scoring |
| Advanced reasoning patterns | 10 techniques with research citations (see Reasoning Techniques section) |
| Responsible AI controls | Policy Guard (5-layer), source-grounding mandate, anti-extrapolation guard, PII blocking, prompt injection detection |
| Hosted deployment story | Dockerfile + azure.yaml + agent.manifest.yaml + server mode. Documented blocker (Azure Student subscription) |

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
# AZURE_SEARCH_ENDPOINT=https://your-search-resource.search.windows.net
# AZURE_SEARCH_API_KEY=your-search-key
# AZURE_SEARCH_INDEX=your-index-name

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

| Feature | Description | Why It Matters |
|---------|-------------|----------------|
| **Multi-Agent Chaining** | Complex requests trigger sequential agent calls (Curator → Study Plan → Engagement) with output passed between agents | Demonstrates multi-step reasoning across agents — directly scores on 25% rubric criterion |
| **REVISE Loop** | When Verifier returns REVISE, the originating agent is re-called with correction guidance automatically | Closed-loop quality guarantee — most submissions just flag and pass through |
| **Routing Confidence** | Mission Control outputs a 0.0–1.0 confidence score. Below 0.6, asks for clarification instead of silently misrouting | Prevents the #1 failure mode in multi-agent systems: wrong agent gets the request |
| **Human Approval Gates** | Study plan generation pauses for user confirmation before proceeding | Enterprise governance requirement — shows human-in-the-loop design |
| **Adaptive Verifier Thresholds** | Assessment: 90% citation required. Plans: 85%. Engagement: 70%. Not a blanket threshold. | Prevents over-blocking on low-risk content while maintaining rigor on high-stakes outputs |
| **Permission-Aware Retrieval** | Knowledge base content access logged with role-level permissions | Simulates Foundry IQ RBAC — production-ready access control |
| **Full Audit Trail** | Every pipeline run logged to JSON: agent calls, routing decisions, governance results, timestamps | IMDA compliance + judges can verify the full reasoning chain |
| **Policy Guard (5-Layer)** | PII → Credentials → Grounding → Injection → Scope. Defence-in-depth safety | Goes beyond "don't hallucinate" — covers 5 distinct attack/failure vectors |
| **Red-Team Testing** | 5 adversarial test scenarios: prompt injection, PII extraction, brain dumps, scope bypass, credential extraction | Validates safety claims empirically, not just architecturally |
| **Source-Grounding Mandate** | Zero unsourced factual claims. Every assertion cites `[source: filename, section]` | Core anti-hallucination control — judges can verify every claim |
| **Anti-Extrapolation Guard** | Agents flag `ASSUMPTION FLAG` when operating beyond grounded evidence | Prevents the most dangerous enterprise AI failure: silently filling knowledge gaps |
| **Few-Shot Constraints** | Each agent includes a CORRECT + INCORRECT output example pair | Anchors quality without fine-tuning — particularly effective on structured tasks |
| **10 Reasoning Techniques** | CoT, ADORE RAG, Abductive, Analogical, Nonmonotonic, Deductive, Self-Consistency, ARM, Layered-CoT, Few-Shot | Research-grounded design with academic citations for every technique |

---

## Agents — Detailed Responsibilities

---

### 1. 🎯 Mission Control Agent — Orchestrator

- **Function:** Classifies user intent via ARM-pattern Chain-of-Thought routing, detects complex multi-agent requests, extracts context (employee ID, team, certification, role), and dispatches to the correct agent or chain.
- **Required input:** User message (natural language).
- **Desired output:** JSON routing decision with `agent`, `employee_id`, `team_id`, `certification`, and `reasoning`. For greetings, returns a direct response.
- **Rejection conditions:** Never answers domain questions directly. If intent is unclear, routes to Learning Path Curator as default. If message is a greeting or out-of-scope small talk, handles directly without calling sub-agents.
- **Chain detection:** Triggers multi-agent chains for complex requests (e.g., "help me prepare" → Curator → Study Plan → Engagement).

---

### 2. 📚 Learning Path Curator Agent — Microsoft Learn / Exam-Tailored

- **Function:** Maps a Microsoft role-based certification target to the correct exam path, skills measured domains, prerequisite/foundation suggestions, and approved learning resources. Grounds all recommendations in the Engineering Certification Guide and live Microsoft Learn search results.
- **Required input:** Role, target certification (optional), experience level (inferred from context), available hours per week (from Work IQ if employee provided).
- **Desired output:** Ordered learning path with certification IDs, exam focus domains, domain-level learning resources, study sequence, estimated hours, and source citations from `engineering_certification_guide.md` and Microsoft Learn API.
- **Rejection agent:** Policy Guard Agent.
- **Rejection conditions:** Reject if the certification code is unknown, if no approved Microsoft Learn-aligned resource is found, or if the request asks for brain dumps / exam cheating content instead of legitimate preparation.
- **IQ Layers:** Foundry IQ (Azure AI Search knowledge base + local certification guide), Microsoft Learn Search API.
- **Reasoning techniques:** ADORE iterative RAG, Chain-of-Thought curation, source-grounding mandate.

---

### 3. 📅 Study Plan Generator Agent — Capacity-Aware Scheduling

- **Function:** Converts a learning path into a personalized, week-by-week study schedule that accounts for the employee's meeting load, focus hours, calendar fragmentation, and preferred learning slot. Flags capacity risks and provides fallback paths.
- **Required input:** Certification target, employee work signals (meeting hours, focus hours, preferred slot), learner progress data (if available), deadline (optional).
- **Desired output:** Week-by-week milestone plan with topics, target practice scores, hours allocated per week, capacity risk assessment, recommended study slot, and fallback path if behind schedule.
- **Rejection agent:** Policy Guard Agent.
- **Rejection conditions:** Reject if employee ID is invalid, if no work signal data exists (returns ASSUMPTION FLAG), or if the requested timeline is physically impossible given workload (flags as CRITICAL_RISK instead of generating unrealistic plan).
- **IQ Layers:** Fabric IQ (business rules, study templates, certification details), Work IQ (employee work patterns).
- **Reasoning techniques:** Chain-of-Thought planning, analogical reasoning (compares to similar learner profiles), nonmonotonic reasoning (revises plan on new constraints), deductive reasoning (applies business rules).

---

### 4. ⏰ Engagement Agent — Work-Context Reminders

- **Function:** Keeps learners progressing by generating personalized, context-aware reminder schedules. Identifies study-safe windows that don't conflict with meetings, adapts tone to workload pressure, and defines escalation triggers when intervention is needed.
- **Required input:** Employee work pattern (meeting hours, focus blocks, preferred slot, fragmentation score), learner progress (practice score, plan completion %).
- **Desired output:** Weekly reminder schedule with specific days/times, recommended tone (encouraging/empathetic/celebratory), sample reminder messages, escalation flag with reason if applicable.
- **Rejection agent:** Policy Guard Agent.
- **Rejection conditions:** Reject if attempting to schedule reminders before 08:00 or after 21:00, during known meeting blocks, or more than 2 reminders per day. If no work signal data exists, falls back to default schedule with ASSUMPTION FLAG.
- **IQ Layers:** Work IQ (employee calendar signals, collaboration load).
- **Reasoning techniques:** Chain-of-Thought scheduling, nonmonotonic reasoning (revises approach if current strategy isn't producing results).

---

### 5. 📝 Assessment Agent — Grounded Question Generation

- **Function:** Evaluates learner readiness by generating scenario-based practice questions grounded in the Engineering Certification Guide. Scores responses against certification pass thresholds and provides a readiness assessment with specific weak domains identified.
- **Required input:** Target certification, skill domains (from context), learner's current practice score (if available).
- **Desired output:** 5 scenario-based multiple-choice questions (A, B, C, D) each citing a source, correct answers with explanations, readiness assessment (READY / BORDERLINE / NOT_READY), and weak domain recommendations.
- **Rejection agent:** Policy Guard Agent.
- **Rejection conditions:** Reject (discard) any question that cannot be mapped to a specific source passage in the knowledge base. If fewer than 5 grounded questions can be generated, return what's available with a gap flag. Reject requests for actual exam answers or brain dumps.
- **IQ Layers:** Foundry IQ (Azure AI Search knowledge base + certification guide + Microsoft Learn API).
- **Reasoning techniques:** ADORE RAG (Claim-Evidence Graph), Chain-of-Thought scoring, source-grounding mandate (zero-tolerance on unsourced questions).

---

### 6. 📊 Manager Insights Agent — Team Analytics

- **Function:** Provides team-level visibility into certification readiness and workforce development. Calculates aggregate metrics, identifies systemic patterns, hypothesizes root causes using abductive reasoning, and generates actionable recommendations — all without exposing individual employee data.
- **Required input:** Team ID (optional — if omitted, reports on all teams). Uses learner performance data and work signals.
- **Desired output:** Team health rating (🟢 GREEN / 🟡 YELLOW / 🔴 RED), aggregate metrics (pass rate, avg score, at-risk count), identified patterns, hypothesized causes, and actionable recommendations.
- **Rejection agent:** Policy Guard Agent.
- **Rejection conditions:** BLOCK if output contains individual employee IDs, names, or personal scores in the team summary. Redirect specific-person queries to aggregate view. If data is null for any field, exclude from analytics with ASSUMPTION FLAG.
- **IQ Layers:** Fabric IQ (team benchmarks, business rules), Work IQ (team-level meeting/focus aggregates).
- **Reasoning techniques:** Chain-of-Thought analytics, abductive reasoning (hypothesizes causes of patterns), deductive reasoning (applies health rating criteria).

---

### 7. 🛡️ Policy Guard Agent — Governance & Safety

- **Function:** Validates all agent outputs before they reach the user through a 5-layer compliance check. Acts as the safety and governance gate for the entire system.
- **Required input:** Any agent output (passed through automatically by the pipeline).
- **Desired output:** Layer-by-layer pass/fail results and an overall status (CLEARED / BLOCKED / FLAGGED).
- **Layers:**
  - Layer 1: PII Scan (real names, emails, phone numbers → BLOCK)
  - Layer 2: Credential Scan (API keys, tokens, passwords → BLOCK)
  - Layer 3: Grounding Compliance (unsourced claims → FLAG for Verifier)
  - Layer 4: Prompt Injection (instruction override attempts → BLOCK)
  - Layer 5: Scope Compliance (out-of-scope advice → BLOCK)
- **Rejection conditions:** Immediately blocks on PII, credentials, injection, or out-of-scope content. Flags grounding issues for Verifier review. When uncertain, returns UNCERTAIN with recommendation for human review.
- **Reasoning techniques:** Layered Chain-of-Thought (arXiv:2501.18645), deductive rule application.

---

### 8. ✅ Verifier Agent — Quality Gate

- **Function:** Final quality validation before response release. Checks citation coverage, reasoning completeness, internal consistency, and assumption count. Uses Self-Consistency CoT (Wang et al. 2022) to cross-validate outputs.
- **Required input:** Agent output (passed through automatically after Policy Guard clears).
- **Desired output:** Verdict (APPROVED / REVISE / ESCALATE) with layer-by-layer scores.
- **Layers:**
  - Layer 1: Citation Coverage (≥85% cited claims required, else REVISE)
  - Layer 2: Reasoning Completeness (all required fields present, else REVISE)
  - Layer 3: Internal Consistency (cert IDs match, employee IDs match, rules applied correctly)
  - Layer 4: Assumption Audit (>3 ASSUMPTION FLAGs → ESCALATE to human review)
- **Rejection conditions:** REVISE if citation coverage <85% or required fields missing. ESCALATE if too many assumptions indicate insufficient grounding. Never releases content that hasn't met quality thresholds.
- **Reasoning techniques:** Self-Consistency CoT (Wang et al. 2022), layered verification chain.

---

## IQ Layer Integration

All three Microsoft IQ layers are actively integrated — Foundry IQ connects to a live Azure AI Search knowledge base, while Fabric IQ and Work IQ are served from structured synthetic data files that model the semantic business layer.

### Foundry IQ — Grounded Enterprise Knowledge

**What it is:** The company's knowledge library. Provides permission-aware, cited retrieval from approved organizational documents.

**How we integrate it:**
- **Azure AI Search** (live connection): The `query_knowledge_base()` tool in `agents/tools.py` queries the `learning-path-curator-resource` Azure AI Search index in real-time. Documents are indexed from Azure Blob Storage (`learningcertstorage`).
- **Local document grounding**: The Engineering Certification Guide (`docs/engineering_certification_guide.md`) is loaded directly into agent context with permission-aware filtering by role.
- **Microsoft Learn Search** (live API): The `search_microsoft_learn()` tool fetches real-time results from Microsoft Learn documentation.

**Used by:** Learning Path Curator, Assessment Agent

**Data sources:**
| Source | Type | Connection |
|--------|------|------------|
| Azure AI Search index (`ks-azureblob-135-index`) | Live API | `AZURE_SEARCH_ENDPOINT` + `AZURE_SEARCH_API_KEY` |
| Microsoft Learn Search API | Live API | Public, no auth required |
| `docs/engineering_certification_guide.md` | Local file | Loaded into agent context |
| `docs/corporate_learning_policy.md` | Local file | Policy grounding |

---

### Fabric IQ — Semantic Business Data Layer

**What it is:** The structured business meaning layer. Models the relationships between roles, certifications, skills, teams, and business rules into a unified semantic model.

**How we integrate it:**
- `data/semantic_model.json` contains the full Fabric IQ semantic layer with:
  - 4 roles with certification mappings and core skills
  - 9 certifications with prerequisites, study hours, pass thresholds, and difficulty levels
  - 5 teams with headcount, meeting averages, and pass rate benchmarks
  - Business rules (meeting thresholds, study targets, exam approval criteria)
  - Study plan templates with week-by-week milestones and target scores
- Agents query this structured data to make grounded decisions (e.g., "Is this employee at risk?" uses the `critical_meeting_threshold` rule)

**Used by:** Study Plan Generator, Manager Insights Agent, Assessment Agent (scoring thresholds)

---

### Work IQ — Work Context and Behavior Signals

**What it is:** Intelligence about how employees actually work — meeting patterns, focus hours, collaboration load, and calendar structure.

**How we integrate it:**
- `data/work_activity_signals.json` contains 18 employee work profiles with:
  - Meeting hours per week
  - Focus hours per week
  - Deep work blocks available
  - Preferred learning time slot (Morning/Afternoon/Evening)
  - Calendar fragmentation score (Low/Medium/High)
  - Average collaboration messages per day
  - Current certification target
- `data/learner_performance.json` contains learning outcomes (practice scores, hours studied, exam results)
- The Engagement Agent uses these signals to schedule reminders in safe windows
- The Study Plan Generator uses them to detect capacity risks and adjust timelines

**Used by:** Engagement Agent, Study Plan Generator, Manager Insights Agent

---

## External Tools & API Integration

The system integrates two external tools that extend agent capabilities beyond local data:

### Microsoft Learn Search API
- **What:** Real-time search of Microsoft's official documentation and certification study guides
- **How:** HTTP GET to `https://learn.microsoft.com/api/search` with query parameters
- **Auth:** None required (public API)
- **Used by:** Learning Path Curator (finds study resources), Assessment Agent (grounds questions in official content)
- **Code:** `agents/tools.py → search_microsoft_learn()`

### Azure AI Search (Foundry IQ Knowledge Base)
- **What:** Queries the organization's indexed knowledge base hosted on Azure AI Search
- **How:** HTTP POST to the search index with keyword search
- **Auth:** API key (`AZURE_SEARCH_API_KEY`)
- **Index:** `ks-azureblob-135-index` containing 15 indexed documents from Azure Blob Storage
- **Used by:** Learning Path Curator, Assessment Agent
- **Code:** `agents/tools.py → query_knowledge_base()`

### Tool Integration Architecture
```
Agent (needs external knowledge)
    ↓
Context Builder in main.py
    ├── search_microsoft_learn(query) → Microsoft Learn API → results injected into prompt
    └── query_knowledge_base(query)  → Azure AI Search API → results injected into prompt
    ↓
Agent receives enriched context with external data + citations
```

---

## Universal Constraints (House Rules)

Every agent enforces these 5 rules (defined in `agents/base.py`). These are non-negotiable system-level constraints that cannot be overridden by any individual agent's instructions:

1. **SOURCE-GROUNDING MANDATE** — Every factual claim must cite `[source: <file>, section: <section>]`. If no source exists, the agent must state "No approved source found. Cannot assert." This is the primary anti-hallucination control.

2. **ANTI-EXTRAPOLATION GUARD** — If the retrieved context is insufficient, agents must explicitly flag: `"ASSUMPTION FLAG: The following is inferred, not retrieved: <statement>"`. This prevents the most dangerous enterprise failure mode: silently filling knowledge gaps with model-generated content that appears authoritative.

3. **CHAIN-OF-THOUGHT MANDATE** — Every response shows STEP 1→4 reasoning before the answer. This makes all agent decisions interpretable, auditable, and verifiable. Judges can see HOW the agent arrived at its conclusion, not just WHAT it concluded.

4. **OUTPUT FORMAT LOCK** — Agents respond in clear, cited natural language. Reasoning is structured (STEP 1→4). Sources are cited inline. This ensures predictable, parseable outputs while remaining human-readable.

5. **REASONING TYPE AWARENESS** — Agents label which reasoning type they apply (deductive, abductive, analogical, nonmonotonic) when it's not purely deductive. This makes the reasoning pattern visible and auditable — judges can verify that the claimed technique is actually being used.

---

## Project Structure

```
├── main.py                          ← Entry point (interactive + server mode)
├── test_scenarios.py                ← Evaluation framework (8 test cases)
├── Dockerfile                       ← Container packaging for Hosted Agent
├── azure.yaml                       ← Azure Developer CLI deployment config
├── agent.manifest.yaml              ← Foundry Agent Service manifest
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
│   ├── verifier.py                  ← Agent 8: Quality
│   └── tools.py                     ← External tool integrations (Microsoft Learn + Azure AI Search)
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
├── requirements.txt                 ← python-dotenv, openai, httpx
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
# Microsoft Foundry Model Endpoint
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT=gpt-oss-120b
AZURE_AI_API_KEY=your-api-key

# Azure AI Search (Foundry IQ Knowledge Base)
AZURE_SEARCH_ENDPOINT=https://your-search-resource.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX=your-index-name
```

---

## Challenge Alignment

| Criterion | Score Weight | How We Address It |
|-----------|-------------|-------------------|
| Accuracy & Relevance | 25% | Source-grounding mandate, live Foundry IQ retrieval via Azure AI Search, Fabric IQ business rules, Microsoft Learn API for real-time content |
| Reasoning & Multi-step Thinking | 25% | CoT in all agents, agent chaining, ARM routing, self-consistency verification, abductive/analogical/nonmonotonic reasoning |
| Creativity & Originality | 15% | 8-agent pipeline with governance layer, ADORE RAG, 10 research-backed reasoning patterns, audit trail system |
| User Experience & Presentation | 15% | Natural language responses, clear pipeline feedback, human approval gates, `audit` command |
| Reliability & Safety | 20% | Policy Guard (5-layer), Verifier, human approval gates, anti-extrapolation guards, permission-aware retrieval |

---

## Known Limitations

- **Hosted Agent deployment:** Azure for Students subscription disables the Azure CLI application (AADSTS7000112), preventing `azd auth login`. The Dockerfile, azure.yaml, and agent.manifest.yaml are included and deployment-ready for a standard Azure subscription.
- **Latency:** Each request makes 3-4 LLM calls (routing + agent + guard + verifier) plus external API calls. Complex chains add more. Average response time is 10-15 seconds per request.
- **Model:** Uses `gpt-oss-120b` which may not always produce perfectly structured output. A gpt-4o deployment would improve reliability and support tool-calling natively.
- **Azure AI Search:** The knowledge base uses keyword search (not semantic search) due to index configuration. In a production setup, semantic ranking would improve retrieval relevance.
- **Work IQ simulation:** Work IQ signals are served from a local JSON file rather than connected to Microsoft 365 Graph API. In production, this would pull real calendar and collaboration data via the Microsoft Graph connector.

---

## Hosted Agent Deployment (Production-Ready)

The system is fully prepared for deployment as a **Foundry Hosted Agent**. All deployment artifacts are included:

### Deployment Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Packages the agent as a container (Python 3.12, port 8088) |
| `azure.yaml` | Azure Developer CLI deployment configuration |
| `agent.manifest.yaml` | Foundry Agent Service registration manifest |

### Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│  Azure Container Registry                           │
│  ┌───────────────────────────────────────────────┐  │
│  │  skillsentinel:latest (Docker image)          │  │
│  │  • Python 3.12 + dependencies                │  │
│  │  • main.py --serve (HTTP mode)               │  │
│  │  • agents/ + data/ + docs/                   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      ↓ Foundry Agent Service pulls image
┌─────────────────────────────────────────────────────┐
│  Foundry Agent Service (Managed Runtime)            │
│  • Provisions compute + Entra ID agent identity     │
│  • Exposes /responses endpoint                      │
│  • Handles scaling, session state, observability    │
│  • Injects APPLICATIONINSIGHTS_CONNECTION_STRING    │
└─────────────────────┬───────────────────────────────┘
                      ↓
              https://[project].services.ai.azure.com/
              api/projects/[project]/agents/skillsentinel-dispatcher
```

### How to Deploy (with standard Azure subscription)

```powershell
# 1. Login
azd auth login

# 2. Install Foundry extension
azd ext install microsoft.foundry

# 3. Provision Azure resources
azd provision

# 4. Build container and deploy
azd deploy

# 5. Test the deployed agent
azd ai agent invoke "What certifications should a Cloud Engineer get?"
```

### Running in Server Mode Locally

```powershell
# Start as HTTP server (same mode used in container)
python main.py --serve

# Test with curl
curl -X POST http://localhost:8088/responses -H "Content-Type: application/json" -d "{\"input\": \"What certs for a Cloud Engineer?\"}"

# Health check
curl http://localhost:8088/health
```

### Why Deployment Was Not Completed

The Azure for Students subscription disables the Azure CLI enterprise application (App ID: `04b07795-8ddb-461a-bbee-02f9e1bf7b46`), which is required for `azd auth login`. This is a tenant-level restriction that cannot be resolved without administrator access. Error: `AADSTS7000112: Application 'Microsoft Azure CLI' is disabled.`

The codebase is fully deployment-ready. With a standard pay-as-you-go or enterprise Azure subscription, deployment would complete in under 5 minutes using the commands above.

---

## License

MIT
