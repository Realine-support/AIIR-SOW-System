"""
Megan's 6-Lever Budget Reduction Hierarchy
Based on email from Megan Marshall (March 4, 2026)

Trigger: "Client budget is lower than the standard program cost"
Apply levers sequentially until budget target is met

Real-world example:
- Standard Ignite: $27,800
- Client constraint: "we do not pay over $25,000"
- Target: $24,900
- Applied levers 1-4 until target reached
"""

from typing import Tuple, List
from app.models import SessionHours, BudgetReduction, ProgramTier


# Budget constraint detection keywords
BUDGET_CONSTRAINT_KEYWORDS = [
    "we've only used independent coaches before",
    "only used independent coaches",
    "our benchmark is around",
    "benchmark is",
    "that price feels high",
    "price feels high",
    "feels high for coaching",
    "we need something more cost-conscious",
    "more cost-conscious",
    "cost-conscious",
    "we like your offering, but it's outside our usual range",
    "outside our usual range",
    "outside our range",
    "typically pay around",
    "usually pay",
    "we do not pay over",
    "don't pay over",
    "do not pay more than",
    "maximum of",
    "budget is",
    "budget ceiling",
    "under budget",
]


def detect_budget_signal(
    budget_constraint_phrases: List[str],
    budget_ceiling: float | None
) -> Tuple[bool, str]:
    """
    Detect if budget reduction should be triggered

    Args:
        budget_constraint_phrases: Phrases from transcript indicating budget sensitivity
        budget_ceiling: Explicit budget max if mentioned (e.g., $25000)

    Returns:
        Tuple of (should_trigger, reason)
    """
    if budget_ceiling and budget_ceiling > 0:
        return True, f"Explicit budget ceiling mentioned: ${budget_ceiling:,.0f}"

    if budget_constraint_phrases and len(budget_constraint_phrases) > 0:
        phrases_str = ", ".join(budget_constraint_phrases[:2])
        return True, f"Budget sensitivity detected: {phrases_str}"

    return False, "No budget constraints detected"


def apply_reduction_hierarchy(
    tier: ProgramTier,
    base_hours: SessionHours,
    bill_rate: float,
    budget_ceiling: float | None,
    current_price: float,
    development_needs_strong: bool = False
) -> Tuple[SessionHours, List[BudgetReduction], float]:
    """
    Apply Megan's 6-lever budget reduction hierarchy

    Levers applied sequentially:
    1. Stakeholder sessions: 1 hr → 0.75 hr
    2. Dev History interview: 2 hr → 1.5 hr
    3. 360° interviews: 6 hr → 4 hr (only if no strong development needs)
    4. Implementation sessions: subtract 1 session
    5. Dev Planning: remove if budget < $35k
    6. Assessment feedback: 2 hr → 1.5 hr

    Args:
        tier: Program tier
        base_hours: Starting session hours (tier defaults)
        bill_rate: Hourly coaching rate
        budget_ceiling: Target budget (if specified)
        current_price: Current calculated price before reductions
        development_needs_strong: If True, don't reduce 360° (lever 3)

    Returns:
        Tuple of (reduced_hours, list_of_reductions_applied, final_price)
    """
    reduced_hours = SessionHours(**base_hours.model_dump())
    reductions: List[BudgetReduction] = []

    # Calculate target price
    if budget_ceiling:
        # Try to get within 5% of budget ceiling
        target_price = budget_ceiling * 0.95
    else:
        # No specific ceiling, apply modest reduction (~10%)
        target_price = current_price * 0.90

    # Track current price as we apply levers
    working_price = current_price

    # === Lever 1: Stakeholder Sessions (1 hr → 0.75 hr) ===
    if working_price > target_price and reduced_hours.stakeholder_sessions_hours >= 1.0:
        original = reduced_hours.stakeholder_sessions_hours
        reduced_hours.stakeholder_sessions_hours = 0.75
        hours_saved = original - reduced_hours.stakeholder_sessions_hours
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=1,
            lever_name="Stakeholder Sessions",
            original_hours=original,
            reduced_hours=reduced_hours.stakeholder_sessions_hours,
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale="Reduced stakeholder meeting from 60 minutes to 45 minutes"
        ))

        working_price -= cost_saved

    # === Lever 2: Developmental History Interview (2 hr → 1.5 hr) ===
    if working_price > target_price and reduced_hours.developmental_history_hours >= 2.0:
        original = reduced_hours.developmental_history_hours
        reduced_hours.developmental_history_hours = 1.5
        hours_saved = original - reduced_hours.developmental_history_hours
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=2,
            lever_name="Developmental History Interview",
            original_hours=original,
            reduced_hours=reduced_hours.developmental_history_hours,
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale="Reduced developmental history interview from 2 hours to 1.5 hours"
        ))

        working_price -= cost_saved

    # === Lever 3: 360° Interviews (6 hr → 4 hr) ===
    # IMPORTANT: "I am making this change based on how much feedback the coachee is looking for.
    # If it seems like they would really benefit from feedback because they have a development
    # opportunity they need to work on, I won't cut the number of interviews."
    if (working_price > target_price and
        reduced_hours.threesixty_interview_hours >= 6.0 and
        not development_needs_strong):

        original = reduced_hours.threesixty_interview_hours
        reduced_hours.threesixty_interview_hours = 4.0  # 6 meetings × 30 min or 8 meetings × 30 min
        hours_saved = original - reduced_hours.threesixty_interview_hours
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=3,
            lever_name="360° Interview Meetings",
            original_hours=original,
            reduced_hours=reduced_hours.threesixty_interview_hours,
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale="Reduced 360° interviews (shorter duration or fewer meetings)"
        ))

        working_price -= cost_saved

    # === Lever 4: Implementation Sessions (subtract 1 session) ===
    if working_price > target_price and reduced_hours.implementation_sessions > 3:
        original_sessions = reduced_hours.implementation_sessions
        reduced_hours.implementation_sessions -= 1

        # Estimate hours per implementation session (typically 1.5 hours)
        hours_saved = 1.5
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=4,
            lever_name="Implementation Sessions",
            original_hours=float(original_sessions),
            reduced_hours=float(reduced_hours.implementation_sessions),
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale=f"Reduced implementation sessions from {original_sessions} to {reduced_hours.implementation_sessions}"
        ))

        working_price -= cost_saved

    # === Lever 5: Dev Planning (remove if budget < $35k) ===
    if (working_price > target_price and
        reduced_hours.dev_planning_hours > 0 and
        (budget_ceiling and budget_ceiling < 35000)):

        original = reduced_hours.dev_planning_hours
        reduced_hours.dev_planning_hours = 0.0
        hours_saved = original
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=5,
            lever_name="Development Planning",
            original_hours=original,
            reduced_hours=0.0,
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale="Removed development planning session due to budget < $35k"
        ))

        working_price -= cost_saved

    # === Lever 6: Assessment Feedback (2 hr → 1.5 hr) ===
    # "Usually one of the last levers we adjust"
    if working_price > target_price and reduced_hours.assessment_feedback_hours >= 2.0:
        original = reduced_hours.assessment_feedback_hours
        reduced_hours.assessment_feedback_hours = 1.5
        hours_saved = original - reduced_hours.assessment_feedback_hours
        cost_saved = hours_saved * bill_rate

        reductions.append(BudgetReduction(
            lever_number=6,
            lever_name="Assessment Feedback Session",
            original_hours=original,
            reduced_hours=reduced_hours.assessment_feedback_hours,
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            rationale="Reduced assessment feedback session from 2 hours to 1.5 hours (last resort lever)"
        ))

        working_price -= cost_saved

    return reduced_hours, reductions, working_price


def calculate_total_hours(hours: SessionHours) -> float:
    """
    Calculate total coaching hours from SessionHours object

    Note: Implementation sessions are not included in total hours here
    because they're counted separately (number of sessions, not hours)

    Returns:
        Total hours of all session types
    """
    return (
        hours.stakeholder_sessions_hours +
        hours.developmental_history_hours +
        hours.threesixty_interview_hours +
        hours.assessment_feedback_hours +
        hours.dev_planning_hours
    )


def estimate_total_price(
    hours: SessionHours,
    bill_rate: float,
    implementation_session_duration: float = 1.0
) -> float:
    """
    Estimate total engagement price

    Args:
        hours: SessionHours object
        bill_rate: Hourly coaching rate
        implementation_session_duration: Estimated hours per implementation session (default 1.0)

    Returns:
        Total estimated price
    """
    # Implementation sessions (estimated hours per session)
    impl_hours = hours.implementation_sessions * implementation_session_duration

    # Other session hours
    other_hours = calculate_total_hours(hours)

    # Total
    total_hours = impl_hours + other_hours
    return total_hours * bill_rate


def generate_reduction_summary(reductions: List[BudgetReduction]) -> str:
    """
    Generate human-readable summary of reductions applied

    Args:
        reductions: List of BudgetReduction objects

    Returns:
        Formatted summary string
    """
    if not reductions:
        return "No budget reductions applied (standard pricing)"

    total_saved = sum(r.cost_saved for r in reductions)
    levers_applied = [f"Lever {r.lever_number}" for r in reductions]

    summary = f"Applied {len(reductions)} budget reduction lever(s): {', '.join(levers_applied)}. "
    summary += f"Total cost reduction: ${total_saved:,.0f}\n\n"

    for r in reductions:
        summary += f"- {r.lever_name}: {r.original_hours} -> {r.reduced_hours} hours "
        summary += f"(saved ${r.cost_saved:,.0f}) - {r.rationale}\n"

    return summary
