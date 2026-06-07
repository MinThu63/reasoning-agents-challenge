from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EngagementAgent:
    def suggest_reminder_window(self, meeting_hours: int, focus_hours: int) -> dict:
        if focus_hours >= 15 and meeting_hours <= 20:
            slot = "afternoon"
        else:
            slot = "morning"
        return {"preferred_slot": slot, "meeting_hours": meeting_hours, "focus_hours": focus_hours}
