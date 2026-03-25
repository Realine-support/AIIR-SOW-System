"""
Tier selection logic for AIIR coaching programs
Maps seniority level + engagement duration to program tier
"""

from typing import Tuple, List
from app.models import SeniorityLevel, ProgramTier


def select_tier(
    seniority_level: SeniorityLevel,
    engagement_duration_months: int | None,
    advisory_flag: bool = False
) -> Tuple[ProgramTier, List[str]]:
    """
    Select appropriate program tier based on seniority and duration

    Args:
        seniority_level: Leadership level of coachee
        engagement_duration_months: Desired duration in months (can be None)
        advisory_flag: True if this is an advisory engagement

    Returns:
        Tuple of (selected_tier, list_of_flags)
        Flags may include warnings like "TIER_AMBIGUOUS_DURATION"

    Logic:
        Advisory → AIIR_VISTA
        C-Suite + 6-12 months → IGNITE
        C-Suite + 4-6 months → ROADMAP
        C-Suite + <4 months → ROADMAP
        Senior + 10+ months → ASCENT
        Senior + 6-9 months → IGNITE
        Senior + <6 months → ROADMAP
        Mid-level + 4-6 months → ROADMAP
        Mid-level + other → SPARK_II
        Early Career + 4-5 months → SPARK_II
        Early Career + 3-4 months → SPARK_I
        Early Career + other → SPARK_I
    """
    flags: List[str] = []

    # Advisory always goes to AIIR VISTA
    if advisory_flag or seniority_level == SeniorityLevel.ADVISORY:
        return ProgramTier.AIIR_VISTA, flags

    # Handle None duration
    if engagement_duration_months is None:
        flags.append("DURATION_NOT_SPECIFIED")
        # Default to mid-tier based on seniority
        if seniority_level == SeniorityLevel.C_SUITE:
            return ProgramTier.ASCENT, flags
        elif seniority_level == SeniorityLevel.SENIOR:
            return ProgramTier.IGNITE, flags
        elif seniority_level == SeniorityLevel.MID_LEVEL:
            return ProgramTier.ROADMAP, flags
        else:  # Early Career
            return ProgramTier.SPARK_I, flags

    # C-Suite logic
    if seniority_level == SeniorityLevel.C_SUITE:
        if 6 <= engagement_duration_months <= 12:
            return ProgramTier.IGNITE, flags
        elif engagement_duration_months >= 4:
            return ProgramTier.ROADMAP, flags
        else:  # < 4 months
            return ProgramTier.ROADMAP, flags

    # Senior level (VP, SVP) logic
    if seniority_level == SeniorityLevel.SENIOR:
        if engagement_duration_months >= 10:
            return ProgramTier.ASCENT, flags
        elif 6 <= engagement_duration_months <= 9:
            return ProgramTier.IGNITE, flags
        else:  # < 6 months
            return ProgramTier.ROADMAP, flags

    # Mid-level (Director) logic
    if seniority_level == SeniorityLevel.MID_LEVEL:
        if 4 <= engagement_duration_months <= 6:
            return ProgramTier.ROADMAP, flags
        else:
            return ProgramTier.SPARK_II, flags

    # Early Career logic
    if seniority_level == SeniorityLevel.EARLY_CAREER:
        if 4 <= engagement_duration_months <= 5:
            return ProgramTier.SPARK_II, flags
        elif 3 <= engagement_duration_months <= 4:
            return ProgramTier.SPARK_I, flags
        else:
            # Default to SPARK_I for very short or unclear durations
            return ProgramTier.SPARK_I, flags

    # Fallback (should never reach here)
    flags.append("TIER_SELECTION_FALLBACK")
    return ProgramTier.ROADMAP, flags


def get_tier_defaults(tier: ProgramTier) -> dict:
    """
    Get default session hours for a given tier (before any reductions)

    Returns:
        Dictionary with default hours for each session type
    """
    defaults = {
        ProgramTier.IGNITE: {
            "implementation_sessions": 8,
            "stakeholder_sessions_hours": 1.0,
            "developmental_history_hours": 2.0,
            "threesixty_interview_hours": 6.0,  # 8 meetings × 45 min
            "assessment_feedback_hours": 2.0,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 7,  # 5-7 month range, default to 7
        },
        ProgramTier.ROADMAP: {
            "implementation_sessions": 5,
            "stakeholder_sessions_hours": 1.0,
            "developmental_history_hours": 2.0,
            "threesixty_interview_hours": 6.0,
            "assessment_feedback_hours": 2.0,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 6,  # 4-6 month range
        },
        ProgramTier.ASCENT: {
            "implementation_sessions": 12,
            "stakeholder_sessions_hours": 1.0,
            "developmental_history_hours": 2.0,
            "threesixty_interview_hours": 6.0,
            "assessment_feedback_hours": 2.0,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 12,  # 8-12 month range
        },
        ProgramTier.SPARK_I: {
            "implementation_sessions": 3,
            "stakeholder_sessions_hours": 0.5,
            "developmental_history_hours": 1.5,
            "threesixty_interview_hours": 4.0,
            "assessment_feedback_hours": 1.5,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 4,  # 3-4 month range
        },
        ProgramTier.SPARK_II: {
            "implementation_sessions": 5,
            "stakeholder_sessions_hours": 1.0,
            "developmental_history_hours": 2.0,
            "threesixty_interview_hours": 5.0,
            "assessment_feedback_hours": 2.0,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 5,  # 4-5 month range
        },
        ProgramTier.AIIR_VISTA: {
            # Advisory tier - custom, these are just placeholders
            "implementation_sessions": 0,
            "stakeholder_sessions_hours": 0.0,
            "developmental_history_hours": 0.0,
            "threesixty_interview_hours": 0.0,
            "assessment_feedback_hours": 0.0,
            "dev_planning_hours": 0.0,
            "coaching_zone_months": 0,
        },
    }

    return defaults.get(tier, defaults[ProgramTier.ROADMAP])
