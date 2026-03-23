"""
Workflow 1 SIMPLIFIED: Transcript to Pricing Review (NO EMAILS)
Orchestrates the complete flow from transcript upload to Google Sheets review

SIMPLIFIED WORKFLOW:
1. Download transcript from Drive
2. Extract variables with OpenAI
3. Calculate pricing using business logic
4. Generate engagement ID
5. Write to Tracker sheet with Status="Pending Review"
6. Write to Calculator sheet
7. Generate pricing rationale
8. Save rationale to Drive
9. Update Tracker with document URLs
10. DONE - Manual review happens in Google Sheets

NO EMAILS, NO WEBHOOKS, NO REDIS STATE
Review happens by updating Status column in Google Sheets manually
"""

from datetime import datetime
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    GoogleDocsService,
    OpenAIService
)
from app.business_logic import calculate_pricing, generate_pricing_rationale
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def process_transcript_to_pricing_simplified(
    file_id: str,
    filename: str,
    config: Config
) -> str:
    """
    Process a new transcript through to pricing review (SIMPLIFIED - NO EMAILS)

    Steps:
    1. Download transcript from Drive
    2. Extract variables with OpenAI
    3. Calculate pricing using business logic
    4. Generate engagement ID
    5. Write to Tracker sheet with Status="Pending Review"
    6. Write to Calculator sheet (detailed breakdown)
    7. Generate pricing rationale (AI + business logic)
    8. Save rationale to Drive
    9. Update Tracker with URLs and Status
    10. DONE - Review happens in Google Sheets

    Args:
        file_id: Google Drive file ID of transcript
        filename: Transcript filename
        config: Application configuration

    Returns:
        Engagement ID
    """
    try:
        logger.info(f"[SIMPLIFIED WORKFLOW] Starting for transcript: {filename} (ID: {file_id})")

        # Initialize services (NO GMAIL, NO REDIS)
        drive = GoogleDriveService(config.google_credentials_path)
        sheets = GoogleSheetsService(config.google_credentials_path)
        docs = GoogleDocsService(config.google_credentials_path)
        openai_svc = OpenAIService(config.openai_api_key)

        # ====================
        # Step 1: Download transcript
        # ====================
        logger.info("Step 1: Downloading transcript from Google Drive")
        transcript_text = drive.download_file(file_id)
        logger.info(f"Downloaded transcript: {len(transcript_text)} characters")

        # ====================
        # Step 2: Extract variables with OpenAI
        # ====================
        logger.info("Step 2: Extracting variables with OpenAI GPT-4o")
        extracted = openai_svc.extract_variables_from_transcript(transcript_text)
        logger.info(f"Extracted variables for: {extracted.client_company_name} - {extracted.coachee_name}")
        logger.info(f"  - Seniority: {extracted.seniority_level.value}")
        logger.info(f"  - Market Type: {extracted.market_type.value}")
        logger.info(f"  - Budget Ceiling: ${extracted.budget_ceiling:,.0f}" if extracted.budget_ceiling else "  - Budget Ceiling: None")
        logger.info(f"  - Self-awareness signals: {len(extracted.self_awareness_signals)}")

        # ====================
        # Step 3: Calculate pricing
        # ====================
        logger.info("Step 3: Calculating pricing with business logic")
        pricing = calculate_pricing(extracted)
        logger.info(f"Pricing calculated:")
        logger.info(f"  - Tier: {pricing.tier.value}")
        logger.info(f"  - Bill Rate: ${pricing.bill_rate_per_hour}/hr")
        logger.info(f"  - Total Hours: {pricing.total_coaching_hours}")
        logger.info(f"  - Total Price: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"  - 360° Decision: {pricing.threesixty_decision}")
        logger.info(f"  - Budget Reductions Applied: {len(pricing.budget_reductions)}")

        # ====================
        # Step 4: Generate engagement ID
        # ====================
        logger.info("Step 4: Generating unique engagement ID")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        client_slug = extracted.client_company_name.replace(' ', '').replace(',', '').upper()[:10]
        engagement_id = f"{client_slug}-{timestamp}"
        logger.info(f"Engagement ID: {engagement_id}")

        # ====================
        # Step 5: Write to Tracker sheet
        # ====================
        logger.info("Step 5: Writing engagement to Tracker sheet")

        # Tracker columns:
        # A: Engagement ID
        # B: Client Company
        # C: Coachee Name
        # D: Coachee Title
        # E: Decision Maker Name
        # F: Decision Maker Email
        # G: Program Tier
        # H: Seniority Level
        # I: Duration (months)
        # J: Market Type
        # K: Bill Rate
        # L: Total Hours
        # M: Total Price
        # N: Payment Terms
        # O: Rationale URL
        # P: Calculator URL
        # Q: SOW URL
        # R: Status
        # S: Created At
        # T: Updated At

        tracker_row = [
            engagement_id,                                          # A
            extracted.client_company_name,                          # B
            extracted.coachee_name,                                 # C
            extracted.coachee_title,                                # D
            extracted.decision_maker_name or extracted.coachee_name, # E
            extracted.decision_maker_email,                         # F
            pricing.tier.value,                                     # G
            str(extracted.seniority_level.value),                   # H
            str(extracted.engagement_duration_months or ''),        # I
            str(extracted.market_type.value),                       # J
            str(pricing.bill_rate_per_hour),                        # K
            str(pricing.total_coaching_hours),                      # L
            str(pricing.total_engagement_price),                    # M
            pricing.payment_terms,                                  # N
            '',  # Rationale URL (will update in step 9)            # O
            '',  # Calculator URL (will update in step 9)           # P
            '',  # SOW URL (not generated yet)                      # Q
            'Pending Review',  # STATUS - Manual review needed      # R
            datetime.now().isoformat(),                             # S - Created At
            datetime.now().isoformat(),                             # T - Updated At
        ]

        sheets.append_row(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            tracker_row
        )
        logger.info(f"✓ Added engagement to Tracker sheet with Status='Pending Review'")

        # ====================
        # Step 6: Write to Calculator sheet
        # ====================
        logger.info("Step 6: Writing detailed breakdown to Calculator sheet")

        calculator_updates = [
            {'range': f'{config.calculator_tab_name}!A2', 'values': [[engagement_id]]},
            {'range': f'{config.calculator_tab_name}!B2', 'values': [[extracted.client_company_name]]},
            {'range': f'{config.calculator_tab_name}!C2', 'values': [[pricing.tier.value]]},
            {'range': f'{config.calculator_tab_name}!D2', 'values': [[pricing.bill_rate_per_hour]]},
            {'range': f'{config.calculator_tab_name}!E2', 'values': [[pricing.session_hours.implementation_sessions]]},
            {'range': f'{config.calculator_tab_name}!F2', 'values': [[pricing.session_hours.stakeholder_sessions_hours]]},
            {'range': f'{config.calculator_tab_name}!G2', 'values': [[pricing.session_hours.developmental_history_hours]]},
            {'range': f'{config.calculator_tab_name}!H2', 'values': [[pricing.session_hours.threesixty_interview_hours]]},
            {'range': f'{config.calculator_tab_name}!I2', 'values': [[pricing.session_hours.assessment_feedback_hours]]},
            {'range': f'{config.calculator_tab_name}!J2', 'values': [[pricing.total_engagement_price]]},
        ]

        sheets.batch_update(config.calculator_sheet_id, calculator_updates)
        calculator_url = f"https://docs.google.com/spreadsheets/d/{config.calculator_sheet_id}"
        logger.info(f"✓ Updated Calculator sheet: {calculator_url}")

        # ====================
        # Step 7: Generate pricing rationale
        # ====================
        logger.info("Step 7: Generating AI-powered pricing rationale")
        rationale_text = generate_pricing_rationale(extracted, pricing)
        logger.info(f"✓ Generated rationale: {len(rationale_text)} characters")

        # ====================
        # Step 8: Save rationale to Drive
        # ====================
        logger.info("Step 8: Saving pricing rationale to Google Drive")
        rationale_filename = f"{engagement_id}_Pricing_Rationale.txt"
        rationale_file_id, rationale_url = drive.upload_file(
            rationale_filename,
            rationale_text,
            config.rationales_folder_id,
            'text/plain'
        )
        logger.info(f"✓ Saved rationale: {rationale_url}")

        # ====================
        # Step 9: Update Tracker with document URLs
        # ====================
        logger.info("Step 9: Updating Tracker with document URLs")
        sheets.update_row_by_engagement_id(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            engagement_id,
            {
                'O': rationale_url,   # Column O: Rationale URL
                'P': calculator_url,  # Column P: Calculator URL
                'T': datetime.now().isoformat(),  # Updated At
            }
        )
        logger.info(f"✓ Updated Tracker with document URLs")

        # ====================
        # DONE!
        # ====================
        logger.info("=" * 80)
        logger.info(f"✓✓✓ WORKFLOW COMPLETED SUCCESSFULLY ✓✓✓")
        logger.info(f"Engagement ID: {engagement_id}")
        logger.info(f"Client: {extracted.client_company_name}")
        logger.info(f"Coachee: {extracted.coachee_name}")
        logger.info(f"Total Price: ${pricing.total_engagement_price:,.0f}")
        logger.info(f"")
        logger.info(f"NEXT STEPS:")
        logger.info(f"1. Open Google Sheets Tracker")
        logger.info(f"2. Review pricing, rationale, and calculator")
        logger.info(f"3. Update Status column to 'Approved' or 'Rejected'")
        logger.info(f"")
        logger.info(f"Tracker: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info(f"Calculator: {calculator_url}")
        logger.info(f"Rationale: {rationale_url}")
        logger.info("=" * 80)

        return engagement_id

    except Exception as e:
        logger.error(f"ERROR in simplified workflow: {e}", exc_info=True)
        raise
