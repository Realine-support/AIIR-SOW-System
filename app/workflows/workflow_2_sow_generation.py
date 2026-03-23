"""
Workflow 2: SOW Generation
Triggered when pricing is approved, generates SOW from template
"""

from datetime import datetime
from jinja2 import Template
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    GoogleDocsService,
    GmailService,
    RedisService
)
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def generate_sow_from_approval(
    engagement_id: str,
    config: Config
) -> str:
    """
    Generate SOW after pricing approval

    Steps:
    1. Read engagement data from Tracker sheet
    2. Create SOW from template
    3. Replace placeholders with engagement data
    4. Save SOW to output folder
    5. Update Tracker with SOW URL
    6. Send SOW review email
    7. Update Redis state to 'sow_review'

    Args:
        engagement_id: Engagement ID
        config: Application configuration

    Returns:
        SOW document ID
    """
    try:
        logger.info(f"Starting SOW generation for engagement: {engagement_id}")

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

        # Step 1: Read engagement data from Tracker
        logger.info("Step 1: Reading engagement data from Tracker")
        row_num = sheets.find_row_by_value(
            config.tracker_sheet_id,
            f"{config.tracker_tab_name}!A:A",
            0,
            engagement_id
        )

        if not row_num:
            raise ValueError(f"Engagement {engagement_id} not found in Tracker")

        # Read the full row
        range_name = f"{config.tracker_tab_name}!A{row_num}:R{row_num}"
        row_data = sheets.read_range(config.tracker_sheet_id, range_name)[0]

        # Parse row data (adjust indices based on actual columns)
        client_company = row_data[1]
        coachee_name = row_data[2]
        coachee_title = row_data[3]
        decision_maker_name = row_data[4]
        decision_maker_email = row_data[5]
        tier = row_data[6]
        total_price = row_data[12]
        payment_terms = row_data[13]

        # Step 2: Create SOW from template
        logger.info("Step 2: Creating SOW from template")
        sow_title = f"SOW_{client_company}_{coachee_name}_{datetime.now().strftime('%Y%m%d')}"

        sow_doc_id, sow_url = docs.create_from_template(
            config.sow_template_doc_id,
            sow_title,
            config.sow_output_folder_id
        )

        # Step 3: Replace placeholders
        logger.info("Step 3: Replacing placeholders in SOW")
        today = datetime.now().strftime("%B %d, %Y")

        replacements = {
            'CLIENT_COMPANY': client_company,
            'COACHEE_NAME': coachee_name,
            'COACHEE_TITLE': coachee_title,
            'PROGRAM_TIER': tier,
            'TOTAL_PRICE': f"${float(total_price):,.0f}",
            'PAYMENT_TERMS': payment_terms,
            'DATE': today,
            'ENGAGEMENT_DURATION': '9 months',  # TODO: Extract from data
            'DECISION_MAKER': decision_maker_name,
        }

        docs.replace_placeholders(sow_doc_id, replacements)

        # Step 4: Update Tracker with SOW URL
        logger.info("Step 4: Updating Tracker with SOW URL")
        sheets.update_row_by_engagement_id(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            engagement_id,
            {
                'P': sow_url,  # Column P: SOW URL
                'Q': 'sow_review',  # Column Q: Status
            }
        )

        # Step 5: Send SOW review email
        logger.info("Step 5: Sending SOW review email")
        with open('templates/sow_review_email.html', 'r') as f:
            email_template = Template(f.read())

        email_html = email_template.render(
            engagement_id=engagement_id,
            client_company_name=client_company,
            coachee_name=coachee_name,
            decision_maker_name=decision_maker_name,
            decision_maker_email=decision_maker_email,
            total_price=f"{float(total_price):,.0f}",
            sow_url=sow_url,
            approve_url=f"{config.approve_sow_webhook_url}?engagement_id={engagement_id}&action=approve",
            reject_url=f"{config.approve_sow_webhook_url}?engagement_id={engagement_id}&action=reject"
        )

        gmail.send_email(
            to=config.review_email_to,
            subject=f"SOW Review: {client_company} - {coachee_name}",
            body=email_html,
            is_html=True
        )

        # Step 6: Update Redis state
        logger.info("Step 6: Updating workflow state in Redis")
        redis.set_state(
            engagement_id,
            'sow_review',
            {
                'sow_doc_id': sow_doc_id,
                'sow_url': sow_url,
                'client': client_company,
                'decision_maker_email': decision_maker_email,
            }
        )

        logger.info(f"SOW generation completed for engagement {engagement_id}")
        return sow_doc_id

    except Exception as e:
        logger.error(f"Error in workflow 2: {e}")
        raise
