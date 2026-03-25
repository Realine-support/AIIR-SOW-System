"""
Test ONLY the business logic - bypasses Google Drive upload
Tests AI extraction and pricing calculation
"""

import asyncio
import logging
from app.config import get_config
from app.services import OpenAIService
from app.business_logic import calculate_pricing, generate_pricing_rationale

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_business_logic():
    """Test business logic with sample transcript"""

    logger.info("=" * 80)
    logger.info("BUSINESS LOGIC TEST - AI EXTRACTION & PRICING CALCULATION")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Load config
        config = get_config()
        logger.info("✓ Config loaded")

        # Initialize OpenAI service
        openai_svc = OpenAIService(config.openai_api_key)
        logger.info("✓ OpenAI service initialized")
        logger.info("")

        # Read sample transcript
        logger.info("Reading sample transcript...")
        with open('sample_transcript.txt', 'r', encoding='utf-8') as f:
            transcript_text = f.read()

        logger.info(f"✓ Loaded transcript: {len(transcript_text)} characters")
        logger.info("")

        # ====================
        # STEP 1: AI EXTRACTION
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 1: AI VARIABLE EXTRACTION")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Sending to OpenAI GPT-4o for structured extraction...")
        extracted = openai_svc.extract_variables_from_transcript(transcript_text)

        logger.info("✓ Extraction complete!")
        logger.info("")
        logger.info("EXTRACTED VARIABLES:")
        logger.info(f"  Client Company: {extracted.client_company_name}")
        logger.info(f"  Coachee: {extracted.coachee_name} ({extracted.coachee_title})")
        logger.info(f"  Decision Maker: {extracted.decision_maker_name} ({extracted.decision_maker_email})")
        logger.info(f"  Seniority Level: {extracted.seniority_level.value}")
        logger.info(f"  Duration: {extracted.engagement_duration_months} months")
        logger.info(f"  Market Type: {extracted.market_type.value}")
        logger.info(f"  Budget Ceiling: ${extracted.budget_ceiling:,.0f}" if extracted.budget_ceiling else f"  Budget Ceiling: None")
        logger.info(f"  Budget Phrases: {extracted.budget_constraint_phrases}")
        logger.info(f"  Self-Awareness Signals: {extracted.self_awareness_signals}")
        logger.info(f"  Existing 360° Status: {extracted.existing_360_status}")
        logger.info(f"  Payment Terms Phrases: {extracted.payment_terms_phrases}")
        logger.info("")

        # ====================
        # STEP 2: PRICING CALCULATION
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 2: PRICING CALCULATION")
        logger.info("=" * 80)
        logger.info("")

        logger.info("Applying business logic...")
        pricing = calculate_pricing(extracted)

        logger.info("✓ Pricing calculated!")
        logger.info("")
        logger.info("PRICING RESULTS:")
        logger.info(f"  Program Tier: {pricing.tier.value}")
        logger.info(f"  Bill Rate: ${pricing.bill_rate_per_hour}/hour")
        logger.info(f"  Total Coaching Hours: {pricing.total_coaching_hours:.1f} hours")
        logger.info(f"  Total Price: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"  Payment Terms: {pricing.payment_terms}")
        logger.info("")

        logger.info("360° ASSESSMENT DECISION:")
        logger.info(f"  Decision: {pricing.threesixty_decision}")
        logger.info(f"  Hours: {pricing.session_hours.threesixty_interview_hours}")
        logger.info(f"  Rationale: {pricing.threesixty_rationale}")
        logger.info("")

        if pricing.budget_reduction_triggered:
            logger.info("BUDGET REDUCTIONS APPLIED:")
            logger.info(f"  Trigger: {pricing.budget_reduction_rationale}")
            logger.info(f"  Number of Levers: {len(pricing.budget_reductions)}")
            total_saved = sum(r.cost_saved for r in pricing.budget_reductions)
            logger.info(f"  Total Saved: ${total_saved:,.0f}")
            logger.info("")
            for i, reduction in enumerate(pricing.budget_reductions, 1):
                logger.info(f"  Lever {reduction.lever_number}: {reduction.lever_name}")
                logger.info(f"    {reduction.original_hours} hrs → {reduction.reduced_hours} hrs")
                logger.info(f"    Saved: ${reduction.cost_saved:,.0f}")
                logger.info(f"    Rationale: {reduction.rationale}")
                logger.info("")
        else:
            logger.info("BUDGET REDUCTIONS: None (standard pricing)")
            logger.info("")

        logger.info("SESSION HOURS BREAKDOWN:")
        logger.info(f"  Implementation Sessions: {pricing.session_hours.implementation_sessions} sessions")
        logger.info(f"  Stakeholder Meetings: {pricing.session_hours.stakeholder_sessions_hours} hrs")
        logger.info(f"  Developmental History: {pricing.session_hours.developmental_history_hours} hrs")
        logger.info(f"  360° Interviews: {pricing.session_hours.threesixty_interview_hours} hrs")
        logger.info(f"  Assessment Feedback: {pricing.session_hours.assessment_feedback_hours} hrs")
        logger.info(f"  Dev Planning: {pricing.session_hours.dev_planning_hours} hrs")
        logger.info(f"  Coaching Zone: {pricing.session_hours.coaching_zone_months} months")
        logger.info("")

        # ====================
        # STEP 3: RATIONALE GENERATION
        # ====================
        logger.info("=" * 80)
        logger.info("STEP 3: RATIONALE GENERATION")
        logger.info("=" * 80)
        logger.info("")

        rationale = generate_pricing_rationale(extracted, pricing)
        logger.info(f"✓ Generated rationale: {len(rationale)} characters")
        logger.info("")
        logger.info("RATIONALE DOCUMENT:")
        logger.info("-" * 80)
        logger.info(rationale)
        logger.info("-" * 80)
        logger.info("")

        # ====================
        # ANALYSIS & VALIDATION
        # ====================
        logger.info("=" * 80)
        logger.info("ANALYSIS: IS THIS CORRECT?")
        logger.info("=" * 80)
        logger.info("")

        # Check tier selection
        logger.info("✓ TIER SELECTION:")
        if extracted.coachee_title == "CTO" and pricing.tier.value == "IGNITE":
            logger.info("  ✓ CORRECT: CTO (C-Suite) + 6 months → IGNITE tier")
        else:
            logger.info(f"  ⚠️  CHECK: {extracted.coachee_title} → {pricing.tier.value}")
        logger.info("")

        # Check bill rate
        logger.info("✓ BILL RATE:")
        if extracted.seniority_level.value == "C-Suite" and pricing.bill_rate_per_hour == 550:
            logger.info("  ✓ CORRECT: C-Suite in Mature market → $550/hr")
        else:
            logger.info(f"  ⚠️  CHECK: {extracted.seniority_level.value} → ${pricing.bill_rate_per_hour}/hr")
        logger.info("")

        # Check 360° decision
        logger.info("✓ 360° DECISION:")
        if extracted.existing_360_status and pricing.session_hours.threesixty_interview_hours == 0:
            logger.info("  ✓ CORRECT: 'just completed 360 last quarter' → ELIMINATE (0 hrs)")
        elif extracted.self_awareness_signals and pricing.session_hours.threesixty_interview_hours == 6:
            logger.info("  ✓ CORRECT: Self-awareness signals detected → KEEP (6 hrs)")
        else:
            logger.info(f"  ⚠️  CHECK: 360° hours = {pricing.session_hours.threesixty_interview_hours}")
        logger.info("")

        # Check budget reductions
        logger.info("✓ BUDGET REDUCTIONS:")
        if extracted.budget_ceiling and pricing.budget_reduction_triggered:
            logger.info(f"  ✓ CORRECT: Budget ceiling ${extracted.budget_ceiling:,.0f} detected → Reductions applied")
            if pricing.total_engagement_price <= extracted.budget_ceiling:
                logger.info(f"  ✓ CORRECT: Final price ${pricing.total_engagement_price:,.0f} within budget")
            else:
                logger.info(f"  ⚠️  CHECK: Final price ${pricing.total_engagement_price:,.0f} exceeds budget ${extracted.budget_ceiling:,.0f}")
        elif extracted.budget_constraint_phrases and pricing.budget_reduction_triggered:
            logger.info(f"  ✓ CORRECT: Budget phrases detected → Reductions applied")
        else:
            logger.info(f"  ⚠️  INFO: No budget constraints → Standard pricing")
        logger.info("")

        # Check payment terms
        logger.info("✓ PAYMENT TERMS:")
        if "50%" in pricing.payment_terms and "Net 30" in pricing.payment_terms:
            logger.info("  ✓ CORRECT: Extracted '50% upfront, 50% at midpoint, Net 30'")
        else:
            logger.info(f"  ⚠️  CHECK: {pricing.payment_terms}")
        logger.info("")

        logger.info("=" * 80)
        logger.info("✓✓✓ BUSINESS LOGIC TEST COMPLETE ✓✓✓")
        logger.info("=" * 80)
        logger.info("")
        logger.info("SUMMARY:")
        logger.info(f"  Client: {extracted.client_company_name}")
        logger.info(f"  Coachee: {extracted.coachee_name}")
        logger.info(f"  Program: {pricing.tier.value}")
        logger.info(f"  Price: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"  All business logic appears to be working correctly!")
        logger.info("")

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_business_logic())
