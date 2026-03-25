"""
Test script to verify business logic implementation
Run this to test the pricing calculator before building the full system

Usage:
    cd aiir-sow-system
    python test_business_logic.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.models import (
    ExtractedVariables,
    SeniorityLevel,
    MarketType,
)
from app.business_logic import calculate_pricing, generate_pricing_rationale


def test_case_1_standard_c_suite():
    """Test Case 1: C-Suite, 9 months, no budget constraints"""
    print("=" * 80)
    print("TEST CASE 1: Standard C-Suite Engagement (No Budget Constraints)")
    print("=" * 80)

    extracted = ExtractedVariables(
        client_company_name="GlobalTech Solutions",
        coachee_name="Amanda Hayes",
        coachee_title="Chief Revenue Officer",
        decision_maker_name="James Chen",
        decision_maker_email="jchen@globaltechsolutions.com",
        seniority_level=SeniorityLevel.C_SUITE,
        engagement_duration_months=9,
        market_type=MarketType.MATURE,
        client_location_city="Boston",
        client_location_state="MA",
        self_awareness_signals=[
            "executive presence",
            "needs honest feedback",
            "stakeholder perception"
        ],
        budget_constraint_phrases=[],
        budget_ceiling=None,
        payment_terms_phrases=[],
    )

    pricing = calculate_pricing(extracted)
    rationale = generate_pricing_rationale(extracted, pricing)

    print(f"\nTier Selected: {pricing.tier.value}")
    print(f"Bill Rate: ${pricing.bill_rate_per_hour}/hour")
    print(f"360° Decision: {pricing.threesixty_decision} ({pricing.session_hours.threesixty_interview_hours} hours)")
    print(f"Budget Reductions Applied: {len(pricing.budget_reductions)}")
    print(f"Total Price: ${pricing.total_engagement_price:,.0f}")
    print(f"Payment Terms: {pricing.payment_terms}")
    print("\n" + "-" * 80)
    print("FULL RATIONALE:")
    print("-" * 80)
    print(rationale)
    print("\n")


def test_case_2_budget_constrained():
    """Test Case 2: C-Suite with budget constraint ($25k ceiling)"""
    print("=" * 80)
    print("TEST CASE 2: Budget-Constrained C-Suite (Megan's Real Example)")
    print("=" * 80)

    extracted = ExtractedVariables(
        client_company_name="Cost-Conscious Corp",
        coachee_name="John Smith",
        coachee_title="Senior Vice President",
        decision_maker_name="Jane Doe",
        decision_maker_email="jdoe@costconscious.com",
        seniority_level=SeniorityLevel.SENIOR,  # Senior level for realistic IGNITE pricing
        engagement_duration_months=8,
        market_type=MarketType.MATURE,
        client_location_city="Chicago",
        client_location_state="IL",
        self_awareness_signals=[],  # No strong signals - triggers 360° reduction
        budget_constraint_phrases=[
            "we do not pay over $25,000 for coaching engagements",
            "that price feels high",
            "need something more cost-conscious"
        ],
        budget_ceiling=10000.0,  # Low ceiling to force budget reductions
        payment_terms_phrases=["50/50 split", "Net 45"],
    )

    pricing = calculate_pricing(extracted)
    rationale = generate_pricing_rationale(extracted, pricing)

    print(f"\nTier Selected: {pricing.tier.value}")
    print(f"Bill Rate: ${pricing.bill_rate_per_hour}/hour")
    print(f"360° Decision: {pricing.threesixty_decision} ({pricing.session_hours.threesixty_interview_hours} hours)")
    print(f"Budget Reductions Applied: {len(pricing.budget_reductions)}")

    if pricing.budget_reductions:
        total_saved = sum(r.cost_saved for r in pricing.budget_reductions)
        print(f"Total Cost Saved: ${total_saved:,.0f}")
        print("Levers Applied:")
        for r in pricing.budget_reductions:
            print(f"  - Lever {r.lever_number}: {r.lever_name} (saved ${r.cost_saved:,.0f})")

    print(f"Total Price: ${pricing.total_engagement_price:,.0f}")
    print(f"Payment Terms: {pricing.payment_terms}")
    print("\n" + "-" * 80)
    print("FULL RATIONALE:")
    print("-" * 80)
    print(rationale)
    print("\n")


def test_case_3_eliminate_360():
    """Test Case 3: Eliminate 360° due to recent completion"""
    print("=" * 80)
    print("TEST CASE 3: Eliminate 360° (Recent 360° Completed)")
    print("=" * 80)

    extracted = ExtractedVariables(
        client_company_name="Tech Startup Inc",
        coachee_name="Sarah Johnson",
        coachee_title="VP of Engineering",
        decision_maker_name="Sarah Johnson",
        decision_maker_email="sjohnson@techstartup.com",
        seniority_level=SeniorityLevel.SENIOR,
        engagement_duration_months=7,
        market_type=MarketType.EMERGING,
        client_location_city="San Francisco",
        client_location_state="CA",
        self_awareness_signals=[],
        existing_360_status="just completed a 360 last quarter",
        budget_constraint_phrases=[],
        budget_ceiling=None,
        payment_terms_phrases=["quarterly payments"],
    )

    pricing = calculate_pricing(extracted)
    rationale = generate_pricing_rationale(extracted, pricing)

    print(f"\nTier Selected: {pricing.tier.value}")
    print(f"Bill Rate: ${pricing.bill_rate_per_hour}/hour")
    print(f"360° Decision: {pricing.threesixty_decision} ({pricing.session_hours.threesixty_interview_hours} hours)")
    print(f"360° Rationale: {pricing.threesixty_rationale}")
    print(f"Budget Reductions Applied: {len(pricing.budget_reductions)}")
    print(f"Total Price: ${pricing.total_engagement_price:,.0f}")
    print(f"Payment Terms: {pricing.payment_terms}")
    print("\n" + "-" * 80)
    print("FULL RATIONALE:")
    print("-" * 80)
    print(rationale)
    print("\n")


def test_case_4_mid_level_roadmap():
    """Test Case 4: Mid-level Director (ROADMAP tier)"""
    print("=" * 80)
    print("TEST CASE 4: Mid-Level Director (ROADMAP Tier)")
    print("=" * 80)

    extracted = ExtractedVariables(
        client_company_name="Manufacturing Co",
        coachee_name="Mike Williams",
        coachee_title="Director of Operations",
        decision_maker_name="VP of HR",
        decision_maker_email="hr@manufacturing.com",
        seniority_level=SeniorityLevel.MID_LEVEL,
        engagement_duration_months=5,
        market_type=MarketType.MATURE,
        client_location_city="Detroit",
        client_location_state="MI",
        self_awareness_signals=["needs to improve", "communication issues"],
        budget_constraint_phrases=[],
        budget_ceiling=None,
        payment_terms_phrases=[],
    )

    pricing = calculate_pricing(extracted)
    rationale = generate_pricing_rationale(extracted, pricing)

    print(f"\nTier Selected: {pricing.tier.value}")
    print(f"Bill Rate: ${pricing.bill_rate_per_hour}/hour")
    print(f"360° Decision: {pricing.threesixty_decision} ({pricing.session_hours.threesixty_interview_hours} hours)")
    print(f"Budget Reductions Applied: {len(pricing.budget_reductions)}")
    print(f"Total Price: ${pricing.total_engagement_price:,.0f}")
    print(f"Payment Terms: {pricing.payment_terms}")
    print("\n" + "-" * 80)
    print("FULL RATIONALE:")
    print("-" * 80)
    print(rationale)
    print("\n")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print(" " * 20 + "AIIR SOW SYSTEM - BUSINESS LOGIC TEST" + " " * 23)
    print("=" * 80)
    print("\n")

    try:
        test_case_1_standard_c_suite()
        test_case_2_budget_constrained()
        test_case_3_eliminate_360()
        test_case_4_mid_level_roadmap()

        print("=" * 80)
        print("SUCCESS: ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext Steps:")
        print("1. Review the pricing calculations above")
        print("2. Verify the 360° decision logic is working correctly")
        print("3. Check that budget reduction levers are applied in the right order")
        print("4. Proceed to implement Google API services and OpenAI integration")
        print("\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n")
