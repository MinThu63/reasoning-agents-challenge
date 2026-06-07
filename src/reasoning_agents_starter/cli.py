from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import settings
from .foundry_cloud import prepare_foundry_client


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _run_local() -> int:
    root = Path(__file__).resolve().parents[2]
    learners_path = root / "data" / "learner_profiles.json"
    work_signals_path = root / "data" / "work_signals.json"

    learners = _load_json(learners_path)
    work_signals = _load_json(work_signals_path)

    print("Reasoning Agents Starter")
    print(f"Model deployment: {settings.azure_ai_model_deployment}")
    print(f"Loaded {len(learners)} synthetic learners and {len(work_signals)} work signals.")
    print("Next step: connect the curator, planner, engagement, assessment, and insights agents.")
    return 0


def _run_cloud() -> int:
    result = prepare_foundry_client()
    print("Reasoning Agents Starter (Cloud Mode)")
    print(f"Project endpoint configured: {result.endpoint}")
    print(f"Model deployment: {result.model_deployment}")
    if result.sdk_ready:
        print("Foundry SDK imports are available.")
    print("Next step: build agent orchestration with Foundry UI or SDK using this endpoint.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Reasoning Agents challenge starter")
    parser.add_argument(
        "--mode",
        choices=["local", "cloud"],
        default="local",
        help="Run local synthetic demo mode or cloud readiness mode.",
    )
    args = parser.parse_args()

    if args.mode == "cloud":
        return _run_cloud()
    return _run_local()
