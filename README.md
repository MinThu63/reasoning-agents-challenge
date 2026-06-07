# Reasoning Agents Starter

Build a multi-agent enterprise learning system using Microsoft Foundry and IQ layers to manage team certification programs.

A synthetic-data-only starter for the Microsoft Foundry Reasoning Agents challenge.

## What this repo gives you

- A Python package skeleton for a multi-agent learning assistant
- Placeholder agents for learning path curation, study planning, engagement, assessment, and manager insights
- Synthetic demo data and synthetic knowledge documents only
- A clean setup path for later wiring to Microsoft Foundry, Foundry IQ, Work IQ, and Fabric IQ

## Project structure

- `src/reasoning_agents_starter/` - application code
- `data/` - synthetic demo inputs
- `docs/` - synthetic reference documents and notes
- `.env.example` - environment variable template

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and set the project endpoint and model deployment name.
4. Run the starter CLI.

Example commands:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m reasoning_agents_starter
```

## Cloud-based development (Microsoft Foundry)

You selected cloud orchestration via Microsoft Foundry.

1. Keep your `.env` with:
   - `AZURE_AI_PROJECT_ENDPOINT`
   - `AZURE_AI_MODEL_DEPLOYMENT`
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run cloud readiness mode:

```powershell
python -m reasoning_agents_starter --mode cloud
```

This verifies your endpoint/deployment configuration and Foundry SDK availability.

## Environment variables

Use synthetic data and keep secrets out of source control.

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT`

Recommended values:

```powershell
AZURE_AI_PROJECT_ENDPOINT=your-project-endpoint-here
AZURE_AI_MODEL_DEPLOYMENT=gpt-4o
```

## Challenge notes

- This starter uses synthetic data only.
- It is intentionally lightweight and is meant to be extended into a hosted or local multi-agent workflow.
- Add grounding, orchestration, and evaluation logic as you connect Microsoft IQ layers.
