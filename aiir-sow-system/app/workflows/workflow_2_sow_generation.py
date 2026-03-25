"""
Workflow 2: SOW Generation (WITH EMAIL NOTIFICATION)
Triggered when pricing model status is approved in tracking sheet,
generates SOW from template and returns email data
"""

from datetime import datetime
from jinja2 import Template
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    GoogleDocsService
)
from app.config import Config
import logging

logger = logging.getLogger(__name__)


async def generate_sow_from_approval(
    engagement_id: str,
    config: Config
) -> dict:
    """
    Generate SOW after pricing model approval

    Steps:
    1. Read engagement data from Tracker sheet
    2. Create SOW from template
    3. Replace placeholders with engagement data
    4. Save SOW to output folder
    5. Update Tracker with SOW URL
    6. Generate email HTML for notification
    7. Return comprehensive data including email

    Args:
        engagement_id: Engagement ID
        config: Application configuration

    Returns:
        dict containing:
            - sow_document_id: str
            - sow_url: str
            - engagement_id: str
            - row_number: int
            - tracking_sheet_url: str
            - email: dict with subject, html_body, to, client_name
    """
    try:
        logger.info(f"Starting SOW generation for engagement: {engagement_id}")

        # Initialize services (NO GMAIL, NO REDIS)
        drive = GoogleDriveService(config.google_credentials_path)
        sheets = GoogleSheetsService(config.google_credentials_path)
        docs = GoogleDocsService(config.google_credentials_path)

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
        range_name = f"{config.tracker_tab_name}!A{row_num}:U{row_num}"
        row_data = sheets.read_range(config.tracker_sheet_id, range_name)[0]

        # Parse row data (SIMPLIFIED DESIGN):
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

        client_company = row_data[2]           # C - Client
        coachee_name = row_data[3]             # D - Coachee
        coachee_title = row_data[4]            # E - Title
        tier = row_data[5]                     # F - Program
        duration = row_data[6] if len(row_data) > 6 else ''  # G - Duration
        total_price_str = row_data[7]          # H - Total Price (includes $ and commas)
        payment_terms = row_data[8]            # I - Payment Terms
        calculator_url = row_data[9] if len(row_data) > 9 else ''  # J - Calculator

        # Extract numeric total_price from formatted string (e.g., "$9,356" -> 9356)
        total_price = total_price_str.replace('$', '').replace(',', '') if total_price_str else '0'

        # For decision maker, we'll need to get it from somewhere else or use coachee
        # Since the simplified sheet doesn't have decision maker columns, we'll extract from other sources
        decision_maker_name = coachee_name  # Use coachee as fallback
        decision_maker_email = ''  # Not in simplified sheet

        # Rationale URL is stored separately, not in main tracker
        rationale_url = ''

        # Step 2: Create SOW from template
        logger.info("Step 2: Creating SOW from template")
        sow_title = f"SOW_{client_company}_{coachee_name}_{datetime.now().strftime('%Y%m%d')}"

        # Create SOW document in the client_documents_folder_id
        sow_doc_id, sow_url = docs.create_from_template(
            config.sow_template_doc_id,
            sow_title,
            config.client_documents_folder_id
        )

        # Step 3: Replace placeholders
        logger.info("Step 3: Replacing placeholders in SOW")
        today = datetime.now().strftime("%B %d, %Y")

        # Map to ALL placeholders in the SOW template
        replacements = {
            # Basic info
            'SOW_DATE': today,
            'HUBSPOT_ID': engagement_id,
            'CLIENT_COMPANY': client_company,
            'CLIENT_TERM': f"{coachee_name}, {coachee_title} at {client_company}",

            # Coaching details
            'STAKEHOLDER_COUNT': '3',
            'COACH_NAME': 'AIIR Consulting',
            'INTERVIEW_COUNT': '8-10 interviews',
            'STREAMS_COUNT': 'three',

            # Program text placeholders
            'DEV_HISTORY_TEXT': 'The coach conducts a comprehensive interview to understand the executive\'s background, goals, and development areas.',
            'ASSESSMENT_FEEDBACK_TEXT': 'Coach meets with the executive to review assessment results and identify key themes and development opportunities.',
            'DEV_PLANNING_TEXT': 'Coach and executive collaborate to create a Strategic Development Plan based on assessment insights.',

            # Financial
            'TOTAL_PRICE': f"${float(total_price):,.0f}",
            'PAYMENT_STRUCTURE': payment_terms,
            'NET_DAYS': '30',
        }

        docs.replace_placeholders(sow_doc_id, replacements)

        # Step 4: Update Tracker with SOW URL
        logger.info("Step 4: Updating Tracker with SOW URL")
        sheets.update_row_by_engagement_id(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            engagement_id,
            {
                'K': sow_url,  # Column K: SOW URL
                'L': 'SOW Generated',  # Column L: Status
            }
        )
        logger.info(f"✓ Updated Tracker with SOW URL in Column K")

        # Step 5: Generate email HTML for notification
        logger.info("Step 5: Generating email notification HTML")

        # Load email template
        with open('templates/sow_generated_email.html', 'r', encoding='utf-8') as f:
            email_template = Template(f.read())

        # Render email HTML
        email_html = email_template.render(
            engagement_id=engagement_id,
            client_company_name=client_company,
            coachee_name=coachee_name,
            coachee_title=coachee_title,
            decision_maker_name=decision_maker_name,
            decision_maker_email=decision_maker_email,
            tier=tier,
            total_price=f"{float(total_price):,.0f}",
            payment_terms=payment_terms,
            sow_url=sow_url,
            tracking_sheet_url=f"https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}",
            calculator_url=calculator_url,
            rationale_url=rationale_url,
            row_number=row_num
        )

        email_subject = f"SOW for {client_company} - Generated and Ready"
        logger.info(f"✓ Email HTML generated")

        # ====================
        # DONE!
        # ====================
        logger.info("=" * 80)
        logger.info(f"✓✓✓ SOW GENERATION COMPLETED SUCCESSFULLY ✓✓✓")
        logger.info(f"Engagement ID: {engagement_id}")
        logger.info(f"Client: {client_company}")
        logger.info(f"Coachee: {coachee_name}")
        logger.info(f"SOW URL: {sow_url}")
        logger.info(f"")
        logger.info(f"NEXT STEPS:")
        logger.info(f"1. Email notification will be sent by n8n")
        logger.info(f"2. Reviewer opens SOW document for final review")
        logger.info(f"3. Once approved, send SOW to client: {decision_maker_email}")
        logger.info(f"")
        logger.info(f"SOW: {sow_url}")
        logger.info(f"Tracker: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info("=" * 80)

        # Return comprehensive data for API response
        return {
            'sow_document_id': sow_doc_id,
            'sow_url': sow_url,
            'engagement_id': engagement_id,
            'row_number': row_num,
            'tracking_sheet_url': f"https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}",
            'calculator_url': calculator_url,
            'rationale_url': rationale_url,
            'email': {
                'subject': email_subject,
                'html_body': email_html,
                'to': config.review_email_to,
                'client_name': client_company,
                'decision_maker_email': decision_maker_email
            },
            'engagement_data': {
                'client_company': client_company,
                'coachee_name': coachee_name,
                'coachee_title': coachee_title,
                'tier': tier,
                'total_price': float(total_price),
                'payment_terms': payment_terms
            }
        }

    except Exception as e:
        logger.error(f"Error in workflow 2: {e}", exc_info=True)
        raise
