from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StudyPlanGenerator:
    def create_plan(self, hours_available: int) -> dict:
        study_blocks = max(1, hours_available // 2)
        return {
            "weekly_hours": hours_available,
            "study_blocks": study_blocks,
            "milestones": ["review role mapping", "practice grounded questions", "take readiness check"],
        }
