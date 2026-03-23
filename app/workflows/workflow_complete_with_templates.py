"""
COMPLETE WORKFLOW: Transcript to Review-Ready Documents
Creates Calculator, SOW, and updates human-friendly Tracker

COMPLETE WORKFLOW:
1. Download transcript from Drive
2. Extract variables with OpenAI
3. Calculate pricing with business logic
4. Generate engagement ID
5. Duplicate Calculator template and populate
6. Duplicate SOW template and populate
7. Update simplified Tracker with all links
8. Status = "Pending Review"
9. Ready for human review!
"""

from datetime import datetime
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    OpenAIService,
    TemplateService
)
from app.business_logic import calculate_pricing, generate_pricing_rationale
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def process_transcript_complete(
    file_id: str,
    filename: str,
    config: Config
) -> str:
    """
    Complete workflow: Transcript → Calculator + SOW + Tracker

    Steps:
    1. Download transcript from Drive
    2. Extract variables with OpenAI
    3. Calculate pricing
    4. Generate engagement ID
    5. Duplicate & populate Calculator template
    6. Duplicate & populate SOW template
    7. Update simplified Tracker
    8. Ready for review!

    Args:
        file_id: Google Drive file ID of transcript
        filename: Transcript filename
        config: Application configuration

    Returns:
        Engagement ID
    """
    try:
        logger.info(f"[COMPLETE WORKFLOW] Starting for: {filename}")
        logger.info("=" * 80)

        # Initialize services
        drive = GoogleDriveService(config.google_credentials_path)
        sheets = GoogleSheetsService(config.google_credentials_path)
        openai_svc = OpenAIService(config.openai_api_key)
        templates = TemplateService(config.google_credentials_path)

        # ====================
        # Step 1: Download transcript
        # ====================
        logger.info("Step 1: Downloading transcript")
        transcript_text = drive.download_file(file_id)
        logger.info(f"✓ Downloaded: {len(transcript_text)} characters")

        # ====================
        # Step 2: AI Extraction
        # ====================
        logger.info("Step 2: AI variable extraction")
        extracted = openai_svc.extract_variables_from_transcript(transcript_text)
        logger.info(f"✓ Extracted: {extracted.client_company_name} - {extracted.coachee_name}")

        # ====================
        # Step 3: Calculate Pricing
        # ====================
        logger.info("Step 3: Calculating pricing")
        pricing = calculate_pricing(extracted)
        logger.info(f"✓ Pricing: {pricing.tier.value} @ ${pricing.total_engagement_price:,.0f}")

        # ====================
        # Step 4: Generate Engagement ID
        # ====================
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        client_slug = extracted.client_company_name.replace(' ', '').replace(',', '').upper()[:10]
        engagement_id = f"{client_slug}-{timestamp}"
        logger.info(f"Step 4: Engagement ID: {engagement_id}")

        # ====================
        # Step 5: Duplicate & Populate Calculator
        # ====================
        logger.info("Step 5: Creating Calculator from template")

        calc_file_id, calc_url = templates.duplicate_calculator_template(
            template_id=config.calculator_template_id,
            client_name=extracted.client_company_name,
            engagement_id=engagement_id,
            destination_folder_id=config.client_master_folder_id
        )

        # Populate calculator with key inputs (bill rate, participants, and actual reduced hours)
        calculator_data = {
            'bill_rate': pricing.bill_rate_per_hour,
            'program_tier': pricing.tier.value,
            'num_participants': 1,  # Default for individual coaching
            'session_hours': pricing.session_hours,  # Pass actual reduced hours from business logic
        }

        templates.populate_calculator(calc_file_id, calculator_data)
        logger.info(f"✓ Calculator populated with inputs")

        # ====================
        # Step 5b: Read Calculated Price from Calculator
        # ====================
        # Calculator is now the SINGLE SOURCE OF TRUTH for pricing
        # Read the final calculated price (includes PM fee, all formulas)
        logger.info("Step 5b: Reading calculated price from Calculator")
        calculated_total_price = templates.read_calculator_total_price(
            file_id=calc_file_id,
            tier=pricing.tier.value
        )
        logger.info(f"✓ Calculator final price: ${calculated_total_price:,.0f}")

        # ====================
        # Step 6: Duplicate & Populate SOW
        # ====================
        logger.info("Step 6: Creating SOW from template")

        sow_doc_id, sow_url = templates.duplicate_sow_template(
            template_id=config.sow_template_doc_id,
            client_name=extracted.client_company_name,
            engagement_id=engagement_id,
            destination_folder_id=config.client_master_folder_id
        )

        # Extract net days from payment terms (e.g., "Net 30")
        net_days = "30"  # Default
        if "net" in pricing.payment_terms.lower():
            import re
            match = re.search(r'net\s*(\d+)', pricing.payment_terms.lower())
            if match:
                net_days = match.group(1)

        # Count stakeholder meetings (typically 4 for IGNITE)
        stakeholder_count = 4  # Default for most programs

        # Calculate interview count from session hours
        interview_count = int(pricing.session_hours.threesixty_interview_hours)
        streams_count = 3  # Standard: 360° data, psychometric results, Developmental History

        # Static session descriptions
        dev_history_text = "A 90-minute conversation exploring the coachee's career journey, formative experiences, and developmental patterns to inform the coaching approach."
        assessment_feedback_text = "A comprehensive debrief of assessment results including 360° feedback and psychometric instruments, identifying key themes and development opportunities."
        dev_planning_text = "Collaborative session to synthesize all assessment data and stakeholder input into a focused development plan with specific goals and success metrics."

        # Prepare SOW data (placeholder replacements matching template)
        sow_data = {
            # Basic Info
            'SOW_DATE': datetime.now().strftime('%B %d, %Y'),
            'CLIENT_COMPANY': extracted.client_company_name,
            'HUBSPOT_ID': engagement_id,  # Using engagement ID as reference
            'CLIENT_TERM': extracted.coachee_name,  # The person being coached

            # Program Details
            'COACH_NAME': 'AIIR Senior Consultant',  # Placeholder - to be assigned
            'STAKEHOLDER_COUNT': str(stakeholder_count),

            # Pricing (from Calculator - single source of truth)
            'TOTAL_PRICE': f'${calculated_total_price:,.0f}',
            'PAYMENT_STRUCTURE': pricing.payment_terms,
            'NET_DAYS': net_days,

            # Session Descriptions (static text)
            'DEV_HISTORY_TEXT': dev_history_text,
            'ASSESSMENT_FEEDBACK_TEXT': assessment_feedback_text,
            'DEV_PLANNING_TEXT': dev_planning_text,
            'INTERVIEW_COUNT': str(interview_count),
            'STREAMS_COUNT': str(streams_count),

            # Additional fields for reference
            'PROGRAM_TIER': pricing.tier.value,
            'COACHEE_NAME': extracted.coachee_name,
            'COACHEE_TITLE': extracted.coachee_title or 'Executive',
            'BILL_RATE': f'${pricing.bill_rate_per_hour}/hour',
            'TOTAL_HOURS': f'{pricing.total_coaching_hours:.1f}',
        }

        # Populate SOW with engagement data
        templates.populate_sow(sow_doc_id, sow_data)
        logger.info(f"✓ SOW created and populated: {sow_url}")

        # ====================
        # Step 7: Generate Rationale (for reference)
        # ====================
        logger.info("Step 7: Generating pricing rationale")
        rationale = generate_pricing_rationale(extracted, pricing)
        logger.info(f"✓ Rationale generated: {len(rationale)} characters")

        # ====================
        # Step 8: Update Simplified Tracker
        # ====================
        logger.info("Step 8: Updating simplified Tracker sheet")

        # Simplified tracker row (14 columns - human-friendly)
        # Using calculated_total_price from Calculator (single source of truth)
        tracker_row = [
            engagement_id,                                          # A: Engagement ID
            datetime.now().strftime('%Y-%m-%d'),                    # B: Date Created
            extracted.client_company_name,                          # C: Client
            extracted.coachee_name,                                 # D: Coachee
            extracted.coachee_title,                                # E: Title
            pricing.tier.value,                                     # F: Program
            f"{extracted.engagement_duration_months or 6} months",  # G: Duration
            f"${calculated_total_price:,.0f}",                      # H: Total Price (from Calculator)
            pricing.payment_terms,                                  # I: Payment Terms
            calc_url,                                               # J: Calculator Link
            sow_url,                                                # K: SOW Link
            '',  # Rationale (optional, can add if needed)          # L: Rationale
            '🟡 Pending Review',                                     # M: Status
            '',  # Notes (empty for reviewer to fill)               # N: Notes
        ]

        sheets.append_row(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            tracker_row
        )
        logger.info(f"✓ Tracker updated with status: Pending Review")

        # ====================
        # DONE!
        # ====================
        logger.info("=" * 80)
        logger.info("✓✓✓ COMPLETE WORKFLOW FINISHED ✓✓✓")
        logger.info("=" * 80)
        logger.info(f"Engagement ID: {engagement_id}")
        logger.info(f"Client: {extracted.client_company_name}")
        logger.info(f"Coachee: {extracted.coachee_name}")
        logger.info(f"Program: {pricing.tier.value}")
        logger.info(f"Price: ${calculated_total_price:,.0f} (from Calculator)")
        logger.info("")
        logger.info("DOCUMENTS CREATED:")
        logger.info(f"  📊 Calculator: {calc_url}")
        logger.info(f"  📄 SOW: {sow_url}")
        logger.info("")
        logger.info("NEXT STEPS:")
        logger.info(f"1. Open Tracker: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info(f"2. Review Calculator and SOW")
        logger.info(f"3. Update Status column to 'Approved' or 'Rejected'")
        logger.info("=" * 80)

        return engagement_id

    except Exception as e:
        logger.error(f"ERROR in complete workflow: {e}", exc_info=True)
        raise
