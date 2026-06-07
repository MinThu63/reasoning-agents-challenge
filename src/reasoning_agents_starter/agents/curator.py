from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LearningPathCurator:
    def suggest_paths(self, certification: str) -> dict:
        return {
            "certification": certification,
            "recommended_topics": ["foundry iq grounding", "role skills", "synthetic practice material"],
            "sources": ["docs/certification_guide.md"],
        }
