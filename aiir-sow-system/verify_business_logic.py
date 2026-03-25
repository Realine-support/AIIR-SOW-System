"""
Comprehensive Business Logic Verification
Verifies all pricing calculations against business rules
"""

from app.business_logic.tier_selection import select_tier, get_tier_defaults
from app.business_logic.bill_rate import calculate_bill_rate
from app.business_logic.pricing_calculator import calculate_pricing
from app.models.extracted_variables import SeniorityLevel, MarketType

print("=" * 80)
print("BUSINESS LOGIC VERIFICATION")
print("=" * 80)

# Test case from transcript: C-Suite, 6 months, Mature market
print("\n1. TIER SELECTION")
print("-" * 80)
seniority = SeniorityLevel.C_SUITE
duration = 6
print(f"Input: Seniority={seniority.value}, Duration={duration} months")

tier, flags = select_tier(seniority, duration)
print(f"Result: {tier.value}")
print(f"Expected: IGNITE (6-month C-Suite engagement)")
print(f"Status: {'PASS' if tier.value == 'IGNITE' else 'FAIL'}")

print("\n2. BILL RATE CALCULATION")
print("-" * 80)
market = MarketType.MATURE
print(f"Input: Seniority={seniority.value}, Market={market.value}")

bill_rate = calculate_bill_rate(seniority, market)
print(f"Result: ${bill_rate}/hour")
print(f"Expected: $550/hour (C-Suite, Mature market)")
print(f"Status: {'PASS' if bill_rate == 550.0 else 'FAIL'}")

print("\n3. SESSION HOURS (TIER DEFAULTS)")
print("-" * 80)
print(f"Input: Tier={tier.value}")

session_hours_dict = get_tier_defaults(tier)
print(f"Results:")
print(f"  - Implementation Sessions: {session_hours_dict['implementation_sessions']}")
print(f"  - Stakeholder Hours: {session_hours_dict['stakeholder_sessions_hours']}")
print(f"  - Dev History Hours: {session_hours_dict['developmental_history_hours']}")
print(f"  - 360 Interview Hours: {session_hours_dict['threesixty_interview_hours']}")
print(f"  - Assessment Feedback Hours: {session_hours_dict['assessment_feedback_hours']}")
print(f"  - Coaching Zone Months: {session_hours_dict['coaching_zone_months']}")

# Verify IGNITE defaults
expected_ignite = {
    'implementation_sessions': 8,
    'stakeholder_hours': 4,
    'dev_history_hours': 2,
    'threesixty_hours': 6,
    'assessment_hours': 2,
    'coaching_zone_months': 9
}

checks = []
checks.append(session_hours_dict['implementation_sessions'] == expected_ignite['implementation_sessions'])
checks.append(session_hours_dict['stakeholder_sessions_hours'] == expected_ignite['stakeholder_hours'])
checks.append(session_hours_dict['developmental_history_hours'] == expected_ignite['dev_history_hours'])
checks.append(session_hours_dict['threesixty_interview_hours'] == expected_ignite['threesixty_hours'])
checks.append(session_hours_dict['assessment_feedback_hours'] == expected_ignite['assessment_hours'])
checks.append(session_hours_dict['coaching_zone_months'] == expected_ignite['coaching_zone_months'])

print(f"\nExpected IGNITE hours match: {'PASS' if all(checks) else 'FAIL'}")

print("\n4. TOTAL PRICING CALCULATION")
print("-" * 80)
print(f"Input: Bill Rate=${bill_rate}/hr, Session Hours from defaults")

# Calculate total hours
total_hours = (
    session_hours_dict['implementation_sessions'] +
    session_hours_dict['stakeholder_sessions_hours'] +
    session_hours_dict['developmental_history_hours'] +
    session_hours_dict['threesixty_interview_hours'] +
    session_hours_dict['assessment_feedback_hours']
)

print(f"Total Coaching Hours: {total_hours}")
print(f"Expected: 22 hours (8+4+2+6+2)")
print(f"Status: {'PASS' if total_hours == 22 else 'FAIL'}")

# Calculate price (without assessments for now)
coach_cost = total_hours * bill_rate
print(f"\nCoach Cost: ${coach_cost:,.0f}")
print(f"Calculation: {total_hours} hours × ${bill_rate}/hr")

# Add PM fee (12%)
pm_fee = coach_cost * 0.12
total_with_pm = coach_cost + pm_fee
print(f"PM Fee (12%): ${pm_fee:,.0f}")
print(f"Total Services Cost: ${total_with_pm:,.0f}")

# Full pricing calculation
from app.models.extracted_variables import ExtractedVariables

# Create test extracted data
extracted = ExtractedVariables(
    client_company_name="TechVision Inc.",
    coachee_name="Michael Chen",
    coachee_title="CTO",
    seniority_level=seniority,
    engagement_duration_months=duration,
    market_type=market,
    decision_maker_name="Sarah Johnson",
    decision_maker_email="sarah@techvision.com",
    threesixty_required=True,
    payment_terms_mentioned="50% upfront, 50% at midpoint, Net 30"
)

pricing = calculate_pricing(extracted)

print(f"\n5. COMPLETE PRICING RESULT")
print("-" * 80)
print(f"Total Engagement Price: ${pricing.total_engagement_price:,.0f}")
print(f"Expected: ~$8,112 (includes coaching, PM fee, assessments)")
print(f"Status: {'PASS' if abs(pricing.total_engagement_price - 8112) < 100 else 'FAIL'}")

print(f"\nPayment Terms: {pricing.payment_terms}")
print(f"Expected: '50% upfront, 50% at midpoint, Net 30 days'")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
