"""
Learning Path Curator Agent (Foundry IQ Grounded)

What it does:
- Suggests relevant learning paths and resources based on role and goals
- Maps certifications to roles with prerequisite chains
- Cites internal knowledge docs (engineering_certification_guide.md)
- Recommends study resources grounded in approved organizational content

Run standalone:
    python agents/learning_path_curator.py
    python agents/learning_path_curator.py --role "Cloud Engineer"
    python agents/learning_path_curator.py --query "What should a Data Engineer study?"
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-oss-120b")
API_KEY = os.getenv("AZURE_AI_API_KEY", "")

DATA_DIR = Path(__file__).parent.parent / "data"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def load_json(filename: str):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_doc(filename: str) -> str:
    with open(DOCS_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt() -> str:
    """Build the Curator's system prompt with Foundry IQ knowledge."""
    semantic_model = load_json("semantic_model.json")
    cert_guide = load_doc("engineering_certification_guide.md")

    cert_list = [
        {"id": c["id"], "name": c["name"], "skills": c["skills_assessed"],
         "hours": c["recommended_study_hours"], "prereqs": c["prerequisites"]}
        for c in semantic_model["certifications"]
    ]

    return f"""You are the Learning Path Curator Agent (Foundry IQ Grounded).
You suggest relevant learning paths and resources based on the learner's role and goals.

YOUR ROLE:
1. Map certification targets to the user's role
2. Recommend prerequisite chains (what to study first)
3. Suggest study resources grounded in approved company documents
4. Cite internal documents by filename when making recommendations

ROLE-CERTIFICATION MAPPING:
{json.dumps(semantic_model['roles'], indent=2)}

CERTIFICATION DETAILS:
{json.dumps(cert_list, indent=2)}

GROUNDING DOCUMENT (Engineering Certification Guide):
{cert_guide[:4000]}

IMPORTANT RULES:
- When citing resources, reference internal documents by filename (e.g., "Source: engineering_certification_guide.md")
- Do NOT invent external URLs or fake links
- If recommending external study, say "Refer to Microsoft Learn official modules" without fabricating specific URLs
- Always mention prerequisites before recommending advanced certs
- Include estimated study hours from the certification details above

All data is synthetic and for demonstration purposes only.
"""


def run_curator(query: str = None, role: str = None):
    """Generate learning path recommendations."""
    from openai import OpenAI

    print("=" * 60)
    print("  LEARNING PATH CURATOR - Foundry IQ Grounded")
    print("=" * 60)
    print()

    if role:
        print(f"  Role: {role}")
    if query:
        print(f"  Query: {query}")
    print()

    base_url = PROJECT_ENDPOINT.split("/api/projects")[0]
    client = OpenAI(
        base_url=f"{base_url}/openai/deployments/{MODEL_DEPLOYMENT}",
        api_key=API_KEY,
        default_headers={"api-key": API_KEY},
        default_query={"api-version": "2024-10-21"},
    )

    system_prompt = build_system_prompt()

    user_message = query or f"What certifications and learning path should a {role or 'Cloud Engineer'} follow? Include prerequisites and estimated study hours."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=messages,
        )
        reply = response.choices[0].message.content
        print(f"🤖 Learning Path Curator:\n\n{reply}")
    except Exception as e:
        error_str = str(e)
        if "'content'" in error_str:
            import ast
            try:
                error_data = ast.literal_eval(error_str.split(" - ", 1)[1])
                reply = error_data["choices"][0]["message"]["content"]
                print(f"🤖 Learning Path Curator:\n\n{reply}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ Error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Learning Path Curator Agent")
    parser.add_argument("--role", default=None, help="Role (e.g., 'Cloud Engineer', 'Data Engineer')")
    parser.add_argument("--query", default=None, help="Free-form question")
    args = parser.parse_args()

    run_curator(query=args.query, role=args.role)


if __name__ == "__main__":
    main()
