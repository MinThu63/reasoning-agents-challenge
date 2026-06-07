from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AssessmentAgent:
    def generate_assessment(self, certification: str) -> dict:
        return {
            "certification": certification,
            "questions": [
                "Explain the main skills covered by the certification.",
                "Describe one realistic scenario where the skill is applied.",
            ],
            "pass_threshold": 75,
        }
