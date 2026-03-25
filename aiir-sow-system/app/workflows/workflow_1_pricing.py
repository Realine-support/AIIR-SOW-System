"""
Workflow 1: Transcript to Pricing Review
Orchestrates the complete flow from transcript upload to pricing review email
"""

from datetime import datetime
from jinja2 import Template
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    GoogleDocsService,
    GmailService,
    RedisService,
    OpenAIService
)
from app.business_logic import calculate_pricing, generate_pricing_rationale
from app.models import EngagementRecord
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def process_transcript_to_pricing(
    file_id: str,
    filename: str,
    config: Config
) -> str:
    """
    Process a new transcript through to pricing review

    Steps:
    1. Download transcript from Drive
    2. Extract variables with OpenAI
    3. Calculate pricing using business logic
    4. Generate engagement ID
    5. Write to Tracker sheet
    6. Write to Calculator sheet (batch update)
    7. Read calculated prices from Calculator
    8. Generate pricing rationale (AI + business logic)
    9. Save rationale to Drive
    10. Update Tracker with URLs
    11. Send review email with approval buttons
    12. Set Redis state to 'pricing_review'

    Args:
        file_id: Google Drive file ID of transcript
        filename: Transcript filename
        config: Application configuration

    Returns:
        Engagement ID
    """
    try:
        logger.info(f"Starting workflow for transcript: {filename} (ID: {file_id})")

        # Initialize services
        drive = GoogleDriveService(config.google_credentials_path)
        sheets = GoogleSheetsService(config.google_credentials_path)
        docs = GoogleDocsService(config.google_credentials_path)
        gmail = GmailService(
            config.google_credentials_path,
            config.gmail_send_as,
            use_oauth2=config.gmail_use_oauth2,
            oauth2_refresh_token=config.gmail_refresh_token,
            oauth2_client_id=config.gmail_client_id,
            oauth2_client_secret=config.gmail_client_secret
        )
        redis = RedisService(config.upstash_redis_rest_url, config.upstash_redis_rest_token)
        openai_svc = OpenAIService(config.openai_api_key)

        # Step 1: Download transcript
        logger.info("Step 1: Downloading transcript")
        transcript_text = drive.download_file(file_id)

        # Step 2: Extract variables with OpenAI
        logger.info("Step 2: Extracting variables with OpenAI")
        extracted = openai_svc.extract_variables_from_transcript(transcript_text)

        # Step 3: Calculate pricing
        logger.info("Step 3: Calculating pricing")
        pricing = calculate_pricing(extracted)

        # Step 4: Generate engagement ID
        logger.info("Step 4: Generating engagement ID")
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        client_slug = extracted.client_company_name.replace(' ', '').upper()[:10]
        engagement_id = f"{client_slug}-{timestamp}"

        # Step 5: Write to Tracker sheet
        logger.info("Step 5: Writing to Tracker sheet")
        tracker_row = [
            engagement_id,
            extracted.client_company_name,
            extracted.coachee_name,
            extracted.coachee_title,
            extracted.decision_maker_name or extracted.coachee_name,
            extracted.decision_maker_email,
            pricing.tier.value,
            str(extracted.seniority_level.value),
            str(extracted.engagement_duration_months or ''),
            str(extracted.market_type.value),
            str(pricing.bill_rate_per_hour),
            str(pricing.total_coaching_hours),
            str(pricing.total_engagement_price),
            pricing.payment_terms,
            '',  # Rationale URL (will update later)
            '',  # SOW URL (will update later)
            'pricing_review',  # Status
            datetime.now().isoformat(),
        ]

        sheets.append_row(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            tracker_row
        )

        # Step 6: Write to Calculator sheet (batch update)
        logger.info("Step 6: Writing to Calculator sheet")
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

        # Step 7: Generate pricing rationale
        logger.info("Step 7: Generating pricing rationale")
        rationale_text = generate_pricing_rationale(extracted, pricing)

        # Step 8: Save rationale to Drive
        logger.info("Step 8: Saving rationale to Drive")
        rationale_filename = f"{engagement_id}_Pricing_Rationale.txt"
        rationale_file_id, rationale_url = drive.upload_file(
            rationale_filename,
            rationale_text,
            config.rationales_folder_id,
            'text/plain'
        )

        # Step 9: Update Tracker with URLs
        logger.info("Step 9: Updating Tracker with document URLs")
        sheets.update_row_by_engagement_id(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            engagement_id,
            {
                'O': rationale_url,  # Column O: Rationale URL
                'P': calculator_url,  # Column P: Calculator URL
            }
        )

        # Step 10: Send review email
        logger.info("Step 10: Sending pricing review email")
        with open('templates/pricing_review_email.html', 'r') as f:
            email_template = Template(f.read())

        email_html = email_template.render(
            engagement_id=engagement_id,
            client_company_name=extracted.client_company_name,
            coachee_name=extracted.coachee_name,
            coachee_title=extracted.coachee_title,
            decision_maker_name=extracted.decision_maker_name or extracted.coachee_name,
            decision_maker_email=extracted.decision_maker_email,
            tier=pricing.tier.value,
            bill_rate=pricing.bill_rate_per_hour,
            total_hours=pricing.total_coaching_hours,
            threesixty_decision=pricing.threesixty_decision,
            threesixty_hours=pricing.session_hours.threesixty_interview_hours,
            budget_reductions=len(pricing.budget_reductions),
            total_price=f"{pricing.total_engagement_price:,.0f}",
            payment_terms=pricing.payment_terms,
            rationale_url=rationale_url,
            calculator_url=calculator_url,
            approve_url=f"{config.approve_pricing_webhook_url}?engagement_id={engagement_id}&action=approve",
            reject_url=f"{config.approve_pricing_webhook_url}?engagement_id={engagement_id}&action=reject"
        )

        gmail.send_email(
            to=config.review_email_to,
            subject=f"Pricing Review: {extracted.client_company_name} - {extracted.coachee_name}",
            body=email_html,
            is_html=True
        )

        # Step 11: Set Redis state
        logger.info("Step 11: Setting workflow state in Redis")
        redis.set_state(
            engagement_id,
            'pricing_review',
            {
                'file_id': file_id,
                'filename': filename,
                'client': extracted.client_company_name,
                'coachee': extracted.coachee_name,
                'price': pricing.total_engagement_price,
            }
        )

        logger.info(f"Workflow completed successfully for engagement {engagement_id}")
        return engagement_id

    except Exception as e:
        logger.error(f"Error in workflow 1: {e}")
        raise
