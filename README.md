# Multi-Agent Enterprise Learning System

> **All data in this repository is synthetic. No real employee names, company data, or PII is included.**

A multi-agent system built for the Microsoft Foundry Reasoning Agents Challenge. It helps organizations manage internal team certification programs through intelligent routing, capacity-aware planning, and grounded knowledge retrieval.

---

## Architecture

```
User Message
     ↓
┌─────────────────────────────┐
│   Entry Agent (Dispatcher)  │  ← Routes to the correct agent
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  📚 Learning Path Curator      (Foundry IQ grounded)    │
│  📅 Study Plan Generator       (Fabric IQ grounded)     │
│  ⏰ Engagement Agent           (Work IQ grounded)       │
│  📝 Assessment Agent           (Foundry IQ grounded)    │
│  📊 Manager Insights Agent     (Fabric IQ + Work IQ)    │
│                                                         │
└─────────────────────────────────────────────────────────┘
              ↓
        Agent Response
```

---

## How It Works

1. User types a message (e.g., "Create a study plan for EMP-034")
2. The **Dispatcher** classifies the intent and routes to the correct agent
3. The specialized agent loads relevant data from the IQ layers
4. The agent calls Azure AI Foundry (gpt-oss-120b) with a grounded system prompt
5. The response is returned to the user

---

## IQ Layer Integration

| Layer | Purpose | Data Source |
|-------|---------|-------------|
| **Foundry IQ** | Grounded knowledge retrieval (company docs) | `docs/` → Azure Blob Storage → Knowledge Base |
| **Fabric IQ** | Semantic business model (roles, certs, rules) | `data/semantic_model.json` |
| **Work IQ** | Employee work patterns and calendar signals | `data/work_activity_signals.json` |

---

## Agents — Detailed Responsibilities

### 1. Entry Agent (Dispatcher)
- Receives all user messages as the single entry point
- Classifies intent (study plan, assessment, engagement, insights, or resource query)
- Extracts context (employee ID, team ID, certification code) from the message
- Routes to the correct specialized agent
- Maintains conversation context across multiple turns
- Does NOT answer questions itself — strictly orchestration only

### 2. Learning Path Curator (Foundry IQ)
- Maps certifications to organizational roles (Cloud Engineer → AZ-204, AZ-305, etc.)
- Identifies prerequisite chains (e.g., AZ-104 before AZ-305)
- Recommends learning resources grounded in the engineering certification guide
- Estimates total study hours per certification
- Cites internal documents by filename — does not fabricate external URLs
- Answers: "What should I study?", "What cert fits my role?", "What are the prerequisites?"

### 3. Study Plan Generator (Fabric IQ)
- Creates personalized week-by-week study schedules with specific milestones
- Loads the employee's work signals (meeting hours, focus hours, preferred slot)
- Adjusts timeline when meeting load exceeds the 20-hour critical threshold
- Includes target practice scores for each milestone week
- Uses study plan templates from the semantic model (AZ-204: 6 weeks, DP-203: 8 weeks, etc.)
- Flags risks and suggests schedule changes if workload threatens study goals
- Answers: "Create a plan for me", "How long will this take?", "I only have 3 weeks"

### 4. Engagement Agent (Work IQ)
- Suggests personalized reminder schedules based on work patterns
- Reads meeting load, focus hours, deep work blocks, and preferred learning slot
- Adapts tone: encouraging if on track, empathetic if struggling
- Avoids sending reminders during peak collaboration hours
- Recommends schedule adjustments when focus hour utilization drops below 75%
- Defines escalation triggers (when to involve the manager)
- Answers: "When should I study?", "Help me stay on track", "I'm struggling with time"

### 5. Assessment Agent (Foundry IQ)
- Generates scenario-based multiple-choice practice questions (A, B, C, D)
- Grounds questions in the engineering certification guide content
- Tests different skill areas per question (no repetition)
- Provides correct answers with explanations after each set
- Evaluates readiness: "Ready" / "Not Ready" / "Borderline" based on scoring thresholds
- Recommends specific focus areas if the learner isn't ready
- Feeds results back into the system (informs study plan adjustments)
- Answers: "Give me practice questions", "Am I ready for AZ-400?", "Quiz me"

### 6. Manager Insights Agent (Fabric IQ + Work IQ)
- Aggregates team-level metrics: pass rate, avg practice score, at-risk count
- Compares team performance against business rule benchmarks
- Highlights capacity-constrained teams (high meeting load → low pass rate)
- Identifies patterns: which teams are struggling and why
- Provides actionable recommendations for managers
- Assigns team health rating (Green / Yellow / Red)
- NEVER exposes individual employee names or personal scores — aggregates only
- Answers: "How is TEAM-D doing?", "Which team is at risk?", "Show me progress"

---

## Project Structure

```
VS/
├── main.py                          ← Orchestrator (run this)
├── agents/
│   ├── learning_path_curator.py
│   ├── study_plan_generator.py
│   ├── engagement_agent.py
│   ├── assessment_agent.py
│   └── manager_insights_agent.py
├── data/
│   ├── learner_performance.json     ← 18 learners with exam outcomes
│   ├── work_activity_signals.json   ← 18 employees with work patterns
│   └── semantic_model.json          ← Roles, certs, teams, rules, templates
├── docs/
│   ├── engineering_certification_guide.md
│   ├── corporate_learning_policy.md
│   └── quarterly_learning_report.md
├── .env                             ← Azure credentials (not committed)
├── .gitignore
├── requirements.txt
└── README.md
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
# Add your Azure AI Foundry endpoint and API key:
#   AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
#   AZURE_AI_MODEL_DEPLOYMENT=gpt-oss-120b
#   AZURE_AI_API_KEY=your-key

# 4. Run the multi-agent system
python main.py
```

---

## Usage

Run `python main.py` and type messages:

```
👤 You: What certifications should a Cloud Engineer get?
  🔄 Dispatcher routing... → 📚 Learning Path Curator

👤 You: Create a study plan for EMP-034
  🔄 Dispatcher routing... → 📅 Study Plan Generator

👤 You: Give me practice questions for AZ-400
  🔄 Dispatcher routing... → 📝 Assessment Agent

👤 You: When should EMP-056 study this week?
  🔄 Dispatcher routing... → ⏰ Engagement Agent

👤 You: How is TEAM-D performing?
  🔄 Dispatcher routing... → 📊 Manager Insights
```

Each agent can also run standalone:

```powershell
python agents/study_plan_generator.py --employee EMP-034
python agents/assessment_agent.py --cert AZ-400 --questions 5
python agents/engagement_agent.py --employee EMP-056
python agents/manager_insights_agent.py --team TEAM-D
python agents/learning_path_curator.py --role "Data Engineer"
```

---

## Synthetic Data

- **Learner IDs:** L-1001 through L-1105 (18 records)
- **Employee IDs:** EMP-001 through EMP-105 (cross-linked)
- **Teams:** TEAM-A through TEAM-E (5 engineering teams)
- **Certifications:** AZ-104, AZ-204, AZ-305, AZ-400, AZ-500, DP-100, DP-203, DP-300, SC-200
- **Roles:** Cloud Engineer, DevOps Engineer, Data Engineer, Security Engineer

---

## Azure AI Foundry Connection

- **Project:** 24036948-0730
- **Model:** gpt-oss-120b (Global Standard deployment)
- **Region:** Japan East
- **Auth:** API Key
- **Knowledge Base:** Created in Azure AI Search (`learning-path-curator-resource`) with docs indexed from Azure Blob Storage (`learningcertstorage`)

---

## Challenge Requirements

- ✅ Multi-agent system with 5 specialized agents + dispatcher
- ✅ Microsoft Foundry SDK integration (model inference via Azure endpoint)
- ✅ Reasoning and multi-step decision-making (dispatcher routes, agents reason over data)
- ✅ At least one Microsoft IQ layer (all three integrated: Foundry IQ, Fabric IQ, Work IQ)
- ✅ Synthetic data only — no PII
- ✅ Demoable with clear agent interactions
- ✅ External tools integration (agents load and reason over structured JSON data)

---

## Limitations

- Foundry IQ knowledge base is configured but cannot be queried directly from agents due to Azure for Students subscription region restrictions (gpt-oss-120b does not support the `data_sources` parameter). Knowledge grounding is achieved through local document loading in agent system prompts.
- In a production deployment with a standard GPT-4o model in a supported region, Foundry IQ would provide cited retrieval directly.
