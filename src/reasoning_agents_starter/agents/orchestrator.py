from __future__ import annotations

from .assessment import AssessmentAgent
from .curator import LearningPathCurator
from .engagement import EngagementAgent
from .insights import ManagerInsightsAgent
from .planner import StudyPlanGenerator


def run_demo_workflow(certification: str, hours_available: int, meeting_hours: int, focus_hours: int) -> dict:
    curator = LearningPathCurator()
    planner = StudyPlanGenerator()
    engagement = EngagementAgent()
    assessment = AssessmentAgent()
    insights = ManagerInsightsAgent()

    path = curator.suggest_paths(certification)
    study_plan = planner.create_plan(hours_available)
    reminder = engagement.suggest_reminder_window(meeting_hours, focus_hours)
    exam = assessment.generate_assessment(certification)
    team_view = insights.summarize_team_status(3)

    return {
        "path": path,
        "study_plan": study_plan,
        "reminder": reminder,
        "assessment": exam,
        "manager_view": team_view,
    }
