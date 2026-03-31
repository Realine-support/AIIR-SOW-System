"""
Pricing Calculator - Orchestrates all business logic
Combines tier selection, bill rate, 360° decision, and budget reductions
"""

from app.models import (
    ExtractedVariables,
    CalculatedPricing,
    SessionHours,
    ProgramTier,
    BudgetReduction,
)
from .tier_selection import select_tier, get_tier_defaults
from .bill_rate import calculate_bill_rate
from .threesixty_decision import decide_360_hours
from .reduction_hierarchy import (
    detect_budget_signal,
    apply_reduction_hierarchy,
    calculate_total_hours,
    estimate_total_price,
    generate_reduction_summary,
)


def calculate_pricing(extracted: ExtractedVariables) -> CalculatedPricing:
    """
    Main pricing calculation orchestrator

    Takes extracted variables from transcript and returns complete pricing calculation
    Applies all business logic in the correct sequence:
    1. Select tier based on seniority + duration
    2. Get tier default hours
    3. Calculate bill rate
    4. Decide on 360° hours (KEEP/REDUCE/ELIMINATE)
    5. Detect budget signals
    6. Apply budget reduction hierarchy if needed
    7. Calculate final pricing

    Args:
        extracted: ExtractedVariables from AI extraction

    Returns:
        CalculatedPricing object with complete pricing breakdown
    """

    # === Step 1: Tier Selection ===
    advisory_flag = (extracted.seniority_level.value == "Advisory")
    tier, tier_flags = select_tier(
        seniority_level=extracted.seniority_level,
        engagement_duration_months=extracted.engagement_duration_months,
        advisory_flag=advisory_flag
    )

    # === Step 2: Get Tier Defaults ===
    defaults = get_tier_defaults(tier)
    base_hours = SessionHours(**defaults)

    # === Step 3: Calculate Bill Rate ===
    bill_rate = calculate_bill_rate(
        seniority_level=extracted.seniority_level,
        market_type=extracted.market_type
    )

    # === Step 4: Decide on 360° Hours ===
    # Check if self-awareness signals suggest strong development needs
    development_needs_strong = len(extracted.self_awareness_signals) > 0

    threesixty_hours, threesixty_decision, threesixty_rationale = decide_360_hours(
        self_awareness_signals=extracted.self_awareness_signals,
        existing_360_status=extracted.existing_360_status,
        budget_signal_detected=False,  # Will determine in next step
        tier_default_360_hours=base_hours.threesixty_interview_hours
    )

    # Update base hours with 360° decision
    base_hours.threesixty_interview_hours = threesixty_hours

    # === Step 5: Detect Budget Signals ===
    budget_signal_detected, budget_signal_reason = detect_budget_signal(
        budget_constraint_phrases=extracted.budget_constraint_phrases,
        budget_ceiling=extracted.budget_ceiling
    )

    # === Step 6: Calculate Initial Price (before reductions) ===
    # Implementation sessions are typically 1.5-2 hours each (using 1.5 as conservative estimate)
    initial_price = estimate_total_price(
        hours=base_hours,
        bill_rate=bill_rate,
        implementation_session_duration=1.5  # Realistic estimate per Megan's pricing
    )

    # === Step 7: Apply Budget Reduction Hierarchy (if needed) ===
    budget_reductions: list[BudgetReduction] = []
    final_hours = base_hours

    if budget_signal_detected:
        final_hours, budget_reductions, reduced_price = apply_reduction_hierarchy(
            tier=tier,
            base_hours=base_hours,
            bill_rate=bill_rate,
            budget_ceiling=extracted.budget_ceiling,
            current_price=initial_price,
            development_needs_strong=development_needs_strong
        )
        final_price = reduced_price
    else:
        final_price = initial_price

    # === Step 8: Calculate Total Hours ===
    total_coaching_hours = calculate_total_hours(final_hours)
    # Add estimated implementation session hours (1.5 hours per session)
    total_coaching_hours += final_hours.implementation_sessions * 1.5

    # === Step 9: Determine Payment Terms ===
    payment_terms = _extract_payment_terms(extracted.payment_terms_phrases)

    # === Step 10: Build CalculatedPricing Object ===
    full_engagement_price = _compute_full_engagement_price(
        final_price, tier, final_hours.coaching_zone_months
    )
    return CalculatedPricing(
        tier=tier,
        tier_selection_flags=tier_flags,
        bill_rate_per_hour=bill_rate,
        session_hours=final_hours,
        budget_reductions=budget_reductions,
        budget_reduction_triggered=budget_signal_detected,
        budget_reduction_rationale=budget_signal_reason if budget_signal_detected else None,
        threesixty_decision=threesixty_decision,
        threesixty_rationale=threesixty_rationale,
        total_coaching_hours=total_coaching_hours,
        total_engagement_price=full_engagement_price,
        price_per_participant=full_engagement_price,  # Single participant
        payment_terms=payment_terms,
    )


def _extract_payment_terms(payment_terms_phrases: list[str]) -> str:
    """
    Extract payment terms from phrases mentioned in transcript

    Default: 100% upfront payment, Net 30 days

    Args:
        payment_terms_phrases: List of payment-related phrases from transcript

    Returns:
        Payment terms string
    """
    if not payment_terms_phrases:
        return "100% upfront payment, Net 30 days"

    # Combine all phrases to analyze
    combined = " ".join(payment_terms_phrases).lower()

    # Check for specific patterns
    if "net 45" in combined or "45 days" in combined:
        net_days = "Net 45 days"
    elif "net 30" in combined or "30 days" in combined:
        net_days = "Net 30 days"
    else:
        net_days = "Net 30 days"  # Default

    # Check for payment split
    if ("50" in combined and ("upfront" in combined or "midpoint" in combined)) or \
       "50/50" in combined or "half now" in combined or "50 percent upfront" in combined:
        return f"50% upfront, 50% at midpoint, {net_days}"
    elif "quarterly" in combined or "installment" in combined:
        return f"Quarterly installments, {net_days}"
    elif "upon completion" in combined or "after delivery" in combined:
        return f"100% upon completion, {net_days}"
    else:
        return f"100% upfront payment, {net_days}"


# Pricing constants (matching Excel calculator)
_PM_FEE_RATE = 0.12         # Project Management fee (12%)
_MARGIN = 0.65              # Services margin (NOTE: Excel cell B16 shows 0.70 but correct is 0.65)
_CZ_RATE_PER_MONTH = 75.0  # Coaching Zone monthly rate (IGNITE F38 corrected value)

# Fixed Assessment Fees per tier
_FIXED_ASSESSMENT_FEES = {
    ProgramTier.IGNITE:    450.0,
    ProgramTier.ROADMAP:   450.0,
    ProgramTier.ASCENT:    450.0,
    ProgramTier.SPARK_I:   450.0,
    ProgramTier.SPARK_II:  450.0,
    ProgramTier.AIIR_VISTA:  0.0,
}


def _compute_full_engagement_price(
    coach_cost: float,
    tier: ProgramTier,
    coaching_zone_months: int,
) -> float:
    """
    Compute TOTAL ENGAGEMENT PRICE from raw coach cost.

    Matches the Excel calculator formula:
      PM Fee             = coach_cost × 0.12
      Services no margin = coach_cost + PM Fee
      Services w/ margin = services_no_margin / (1 - 0.65)
      CZ Fee             = coaching_zone_months × $75
      Fixed Fees         = tier-specific fixed assessment fees
      TOTAL              = services_w_margin + CZ Fee + Fixed Fees
    """
    pm_fee = coach_cost * _PM_FEE_RATE
    services_no_margin = coach_cost + pm_fee
    services_with_margin = services_no_margin / (1.0 - _MARGIN)
    cz_fee = coaching_zone_months * _CZ_RATE_PER_MONTH
    fixed_fees = _FIXED_ASSESSMENT_FEES.get(tier, 450.0)
    return round(services_with_margin + cz_fee + fixed_fees, 2)


def generate_pricing_rationale(
    extracted: ExtractedVariables,
    pricing: CalculatedPricing
) -> str:
    """
    Generate human-readable pricing rationale document

    This is what gets saved as a Google Doc and sent to the review team

    Args:
        extracted: Extracted variables from transcript
        pricing: Calculated pricing

    Returns:
        Formatted rationale text (markdown-style)
    """
    rationale = []

    # Header
    rationale.append(f"# Pricing Rationale: {extracted.client_company_name}")
    rationale.append(f"**Coachee:** {extracted.coachee_name} ({extracted.coachee_title})")
    rationale.append(f"**Decision Maker:** {extracted.decision_maker_name or 'TBD'}")
    rationale.append("")

    # Tier Selection
    rationale.append("## Program Tier Selection")
    rationale.append(f"**Selected Tier:** {pricing.tier.value}")
    rationale.append(f"**Seniority Level:** {extracted.seniority_level.value}")
    rationale.append(f"**Engagement Duration:** {extracted.engagement_duration_months} months")
    rationale.append(f"**Market Type:** {extracted.market_type.value}")

    if pricing.tier_selection_flags:
        rationale.append(f"**Flags:** {', '.join(pricing.tier_selection_flags)}")
    rationale.append("")

    # Bill Rate
    rationale.append("## Bill Rate Calculation")
    rationale.append(f"**Hourly Rate:** ${pricing.bill_rate_per_hour}/hour")
    rationale.append(f"**Basis:** {extracted.seniority_level.value} level in {extracted.market_type.value} market")
    rationale.append("")

    # 360° Decision
    rationale.append("## 360° Assessment Decision")
    rationale.append(f"**Decision:** {pricing.threesixty_decision}")
    rationale.append(f"**Hours Allocated:** {pricing.session_hours.threesixty_interview_hours}")
    rationale.append(f"**Rationale:** {pricing.threesixty_rationale}")

    if extracted.self_awareness_signals:
        rationale.append(f"**Signals Detected:** {', '.join(extracted.self_awareness_signals[:5])}")
    if extracted.existing_360_status:
        rationale.append(f"**Existing 360° Status:** {extracted.existing_360_status}")
    rationale.append("")

    # Budget Reductions
    if pricing.budget_reduction_triggered:
        rationale.append("## Budget Reductions Applied")
        rationale.append(f"**Trigger:** {pricing.budget_reduction_rationale}")

        if extracted.budget_ceiling:
            rationale.append(f"**Budget Ceiling:** ${extracted.budget_ceiling:,.0f}")
        if extracted.budget_constraint_phrases:
            rationale.append(f"**Budget Signals:** {', '.join(extracted.budget_constraint_phrases[:3])}")

        rationale.append("")
        rationale.append(generate_reduction_summary(pricing.budget_reductions))
    else:
        rationale.append("## Budget Reductions")
        rationale.append("No budget reductions applied (standard pricing)")
        rationale.append("")

    # Session Hours Breakdown
    rationale.append("## Session Hours Breakdown")
    rationale.append(f"- Implementation Sessions: {pricing.session_hours.implementation_sessions} sessions")
    rationale.append(f"- Stakeholder Meetings: {pricing.session_hours.stakeholder_sessions_hours} hours")
    rationale.append(f"- Developmental History: {pricing.session_hours.developmental_history_hours} hours")
    rationale.append(f"- 360° Interviews: {pricing.session_hours.threesixty_interview_hours} hours")
    rationale.append(f"- Assessment Feedback: {pricing.session_hours.assessment_feedback_hours} hours")
    if pricing.session_hours.dev_planning_hours > 0:
        rationale.append(f"- Development Planning: {pricing.session_hours.dev_planning_hours} hours")
    rationale.append(f"- Coaching Zone Access: {pricing.session_hours.coaching_zone_months} months")
    rationale.append("")

    # Total Pricing
    rationale.append("## Total Pricing")
    rationale.append(f"**Total Coaching Hours:** {pricing.total_coaching_hours:.1f} hours")
    rationale.append(f"**Hourly Rate:** ${pricing.bill_rate_per_hour}/hour")
    rationale.append(f"**Total Engagement Price:** ${pricing.total_engagement_price:,.0f}")
    rationale.append(f"**Payment Terms:** {pricing.payment_terms}")
    rationale.append("")

    # Special Flags
    if extracted.tes_addon_requested:
        rationale.append("⚠️ **Team Effectiveness (TES) add-on mentioned** - Requires manual pricing review")
    if extracted.msa_rate_card_mentioned:
        rationale.append("⚠️ **MSA rate card mentioned** - May need to override bill rate")
    if extracted.custom_template_requested:
        rationale.append("⚠️ **Custom client SOW template requested** - Manual SOW generation required")

    return "\n".join(rationale)
