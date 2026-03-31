"""
Workflow 1 SIMPLIFIED: Transcript to Pricing Review (WITH EMAIL NOTIFICATION)
Orchestrates the complete flow from transcript upload to pricing model review

UPDATED WORKFLOW:
1. Download transcript from Drive
2. Extract variables with OpenAI
3. Calculate pricing using business logic
4. Generate engagement ID
5. Write to Tracker sheet with Status="Pending Review" and Pricing Model Status="Pending Review"
6. Write to Calculator sheet
7. Generate pricing rationale
8. Save rationale to Drive
9. Update Tracker with document URLs
10. Generate email HTML body for notification
11. Return engagement data + email data for n8n to send

EMAIL NOTIFICATION ADDED
Review happens by updating "Pricing Model Status" column in Google Sheets manually
"""

from datetime import datetime
from jinja2 import Template
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    GoogleDocsService,
    OpenAIService
)
from app.services.google_services import GoogleServicesManager
from app.business_logic import calculate_pricing, generate_pricing_rationale
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def process_transcript_to_pricing_simplified(
    file_id: str,
    filename: str,
    config: Config
) -> dict:
    """
    Process a new transcript through to pricing review (WITH EMAIL NOTIFICATION)

    Steps:
    1. Download transcript from Drive
    2. Extract variables with OpenAI
    3. Calculate pricing using business logic
    4. Generate engagement ID
    5. Write to Tracker sheet with Status="Pending Review" and Pricing Model Status="Pending Review"
    6. Write to Calculator sheet (detailed breakdown)
    7. Generate pricing rationale (AI + business logic)
    8. Save rationale to Drive
    9. Update Tracker with URLs and Status
    10. Generate email HTML for notification
    11. Return engagement data + email data

    Args:
        file_id: Google Drive file ID of transcript
        filename: Transcript filename
        config: Application configuration

    Returns:
        dict containing:
            - engagement_id: str
            - row_number: int
            - tracking_sheet_url: str
            - calculator_url: str
            - rationale_url: str
            - email: dict with subject, html_body, to, client_name
    """
    try:
        logger.info(f"[SIMPLIFIED WORKFLOW] Starting for transcript: {filename} (ID: {file_id})")

        # Initialize services (NO GMAIL, NO REDIS)
        # Use GoogleServicesManager to handle credentials (supports both JSON and file path)
        google_manager = GoogleServicesManager(config)
        drive = GoogleDriveService(google_manager.get_drive_service())
        sheets = GoogleSheetsService(google_manager.get_sheets_service())
        docs = GoogleDocsService(google_manager.get_docs_service(), google_manager.get_drive_service())
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

        # Tracker columns (SIMPLIFIED DESIGN - matching actual sheet structure):
        # A: Engagement ID
        # B: Date Created
        # C: Client
        # D: Coachee
        # E: Title
        # F: Program
        # G: Duration
        # H: Total Price
        # I: Payment Terms
        # J: Calculator
        # K: SOW
        # L: Status
        # M: Notes
        # N-T: (empty columns)
        # U: Pricing Model Status

        tracker_row = [
            engagement_id,                                          # A - Engagement ID
            datetime.now().strftime("%Y-%m-%d"),                    # B - Date Created
            extracted.client_company_name,                          # C - Client
            extracted.coachee_name,                                 # D - Coachee
            extracted.coachee_title,                                # E - Title
            pricing.tier.value,                                     # F - Program
            f"{extracted.engagement_duration_months or ''} months", # G - Duration
            f"${pricing.total_engagement_price:,.0f}",              # H - Total Price
            pricing.payment_terms,                                  # I - Payment Terms
            '',  # Calculator URL (will update in step 9)           # J - Calculator
            '',  # SOW URL (not generated yet - stays empty)        # K - SOW
            'Pending Review',  # STATUS                             # L - Status
            '',  # Notes (empty for user to fill)                   # M - Notes
            '',  # N (empty)
            '',  # O (empty)
            '',  # P (empty)
            '',  # Q (empty)
            '',  # R (empty)
            '',  # S (empty)
            '',  # T (empty)
            'Pending Review',  # PRICING MODEL STATUS               # U - Pricing Model Status
        ]

        # Specify the exact column range to append to (A:U)
        # This ensures the row is appended to the correct columns, not to hidden columns
        sheets.append_row(
            config.tracker_sheet_id,
            f"{config.tracker_tab_name}!A:U",
            tracker_row
        )
        logger.info(f"✓ Added engagement to Tracker sheet with Status='Pending Review'")

        # ====================
        # Step 6: Write to Calculator sheet
        # ====================
        logger.info("Step 6: Writing detailed breakdown to Calculator sheet")

        # Create a per-engagement copy of the calculator template
        raw_drive = google_manager.get_drive_service()
        copied_sheet = raw_drive.files().copy(
            fileId=config.calculator_template_id,
            body={
                'name': f"Calculator_{engagement_id}",
                'parents': [config.client_documents_folder_id],
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            },
            fields='id,webViewLink',
            supportsAllDrives=True
        ).execute()
        per_engagement_sheet_id = copied_sheet['id']
        calculator_url = copied_sheet['webViewLink']
        logger.info(f"✓ Created per-engagement Calculator sheet: {calculator_url}")

        # Populate the calculator with engagement-specific values
        # Tab name is "Coaching Calculator" (from Excel template structure)
        # Cell positions match the actual Excel template layout
        calculator_updates = [
            {'range': 'Coaching Calculator!B15', 'values': [[pricing.bill_rate_per_hour]]},
            {'range': 'Coaching Calculator!B16', 'values': [[0.65]]},  # Correct margin (template default 0.70 is wrong)
            {'range': 'Coaching Calculator!B39', 'values': [[pricing.session_hours.developmental_history_hours]]},
            {'range': 'Coaching Calculator!B40', 'values': [[pricing.session_hours.threesixty_interview_hours]]},
            {'range': 'Coaching Calculator!B41', 'values': [[pricing.session_hours.assessment_feedback_hours]]},
            {'range': 'Coaching Calculator!B44', 'values': [[pricing.session_hours.implementation_sessions]]},
            {'range': 'Coaching Calculator!E37', 'values': [[pricing.session_hours.coaching_zone_months]]},
        ]
        try:
            sheets.batch_update(per_engagement_sheet_id, calculator_updates)
            logger.info(f"✓ Populated Calculator sheet with engagement values")
        except Exception as calc_err:
            logger.warning(f"Could not populate Calculator cells (template defaults will show): {calc_err}")

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
                'J': calculator_url,  # Column J: Calculator URL
                # Note: Column K (SOW) stays empty until workflow 2
                # Rationale URL stored separately, not in main tracker view
            }
        )
        logger.info(f"✓ Updated Tracker with Calculator URL")

        # ====================
        # Step 10: Get row number for the engagement
        # ====================
        logger.info("Step 10: Finding engagement row number in Tracker")
        row_number = sheets.find_row_by_value(
            config.tracker_sheet_id,
            f"{config.tracker_tab_name}!A:A",
            0,
            engagement_id
        )
        logger.info(f"✓ Engagement is in row {row_number}")

        # ====================
        # Step 11: Generate email HTML for notification
        # ====================
        logger.info("Step 11: Generating email notification HTML")

        # Load email template
        with open('templates/pricing_model_ready_email.html', 'r', encoding='utf-8') as f:
            email_template = Template(f.read())

        # Render email HTML
        email_html = email_template.render(
            engagement_id=engagement_id,
            client_company_name=extracted.client_company_name,
            coachee_name=extracted.coachee_name,
            coachee_title=extracted.coachee_title,
            decision_maker_name=extracted.decision_maker_name or extracted.coachee_name,
            decision_maker_email=extracted.decision_maker_email or extracted.coachee_email or "noemail@placeholder.com",
            tier=pricing.tier.value,
            bill_rate=pricing.bill_rate_per_hour,
            total_hours=pricing.total_coaching_hours,
            threesixty_decision=pricing.threesixty_decision,
            threesixty_hours=pricing.session_hours.threesixty_interview_hours,
            budget_reductions=len(pricing.budget_reductions),
            total_price=f"{pricing.total_engagement_price:,.0f}",
            payment_terms=pricing.payment_terms,
            tracking_sheet_url=f"https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}",
            calculator_url=calculator_url,
            rationale_url=rationale_url,
            row_number=row_number
        )

        email_subject = f"Pricing Model for {extracted.client_company_name} - Ready for Review"
        logger.info(f"✓ Email HTML generated")

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
        logger.info(f"1. Email notification will be sent by n8n")
        logger.info(f"2. Reviewer opens Tracking Sheet and reviews pricing")
        logger.info(f"3. Reviewer updates 'Pricing Model Status' (Column U) to 'Approved' or 'Disapproved'")
        logger.info(f"4. If Approved, SOW generation will be triggered automatically")
        logger.info(f"")
        logger.info(f"Tracker: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info(f"Calculator: {calculator_url}")
        logger.info(f"Rationale: {rationale_url}")
        logger.info("=" * 80)

        # Return comprehensive data for API response
        return {
            'engagement_id': engagement_id,
            'row_number': row_number,
            'tracking_sheet_url': f"https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}",
            'calculator_url': calculator_url,
            'rationale_url': rationale_url,
            'email': {
                'subject': email_subject,
                'html_body': email_html,
                'to': config.review_email_to,
                'client_name': extracted.client_company_name
            },
            'pricing_data': {
                'tier': pricing.tier.value,
                'total_price': pricing.total_engagement_price,
                'total_hours': pricing.total_coaching_hours,
                'bill_rate': pricing.bill_rate_per_hour
            }
        }

    except Exception as e:
        logger.error(f"ERROR in simplified workflow: {e}", exc_info=True)
        raise
