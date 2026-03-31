"""
Workflow 1 SIMPLIFIED: Transcript to Pricing Review (WITH EMAIL NOTIFICATION)
Orchestrates the complete flow from transcript upload to pricing model review

UPDATED WORKFLOW:
1. Download transcript from Drive
2. Extract variables with OpenAI
3. Calculate pricing inputs using business logic
4. Generate engagement ID
5. Copy calculator template + write all input cells
6. Read total price back from calculator sheet (sheet formulas are source of truth)
7. Write to Tracker sheet with sheet-sourced total
8. Generate pricing rationale
9. Save rationale to Drive
10. Update Tracker with document URLs
11. Generate email HTML body for notification
12. Return engagement data + email data for n8n to send

The calculator sheet owns all price math (PM fee, margin, CZ fee, assessment fees).
Python only writes inputs; the sheet computes the total.
"""

from datetime import datetime
from jinja2 import Template
from app.services import (
    GoogleDriveService,
    GoogleSheetsService,
    OpenAIService
)
from app.services.google_services import GoogleServicesManager
from app.business_logic import calculate_pricing, generate_pricing_rationale
from app.models import ProgramTier
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cell maps — per tier, "Coaching Calculator" tab
# Keys match SessionHours field names where applicable.
# ---------------------------------------------------------------------------

_TIER_INPUT_CELLS = {
    ProgramTier.ROADMAP: {
        'cz_months':      'Coaching Calculator!E21',
        'stakeholder':    'Coaching Calculator!B22',
        'dev_history':    'Coaching Calculator!B23',
        'assessment':     'Coaching Calculator!B24',
        'dev_planning':   'Coaching Calculator!B25',
        'impl_sessions':  'Coaching Calculator!B27',
    },
    ProgramTier.IGNITE: {
        'cz_months':      'Coaching Calculator!E37',
        'stakeholder':    'Coaching Calculator!B38',
        'dev_history':    'Coaching Calculator!B39',
        'threesixty':     'Coaching Calculator!B40',
        'assessment':     'Coaching Calculator!B41',
        'dev_planning':   'Coaching Calculator!B42',
        'impl_sessions':  'Coaching Calculator!B44',
    },
    ProgramTier.ASCENT: {
        'cz_months':      'Coaching Calculator!E55',
        'stakeholder':    'Coaching Calculator!B56',
        'dev_history':    'Coaching Calculator!B57',
        'threesixty':     'Coaching Calculator!B58',
        'assessment':     'Coaching Calculator!B59',
        'dev_planning':   'Coaching Calculator!B60',
        'impl_sessions':  'Coaching Calculator!B62',
    },
    ProgramTier.SPARK_I: {
        'cz_months':      'Coaching Calculator!E73',
        'stakeholder':    'Coaching Calculator!B74',
        'assessment':     'Coaching Calculator!B75',
        'dev_planning':   'Coaching Calculator!B76',
        'impl_sessions':  'Coaching Calculator!B77',
    },
    ProgramTier.SPARK_II: {
        'cz_months':      'Coaching Calculator!E91',
        'stakeholder':    'Coaching Calculator!B92',
        'dev_history':    'Coaching Calculator!B93',
        'assessment':     'Coaching Calculator!B94',
        'dev_planning':   'Coaching Calculator!B95',
        'impl_sessions':  'Coaching Calculator!B97',
    },
    ProgramTier.AIIR_VISTA: {},  # AIIR Vista uses template defaults; no variable inputs
}

# "Engagement Total Per Participant" cell per tier — this is what we read back
_TIER_TOTAL_CELL = {
    ProgramTier.ROADMAP:    'Coaching Calculator!H30',
    ProgramTier.IGNITE:     'Coaching Calculator!H48',
    ProgramTier.ASCENT:     'Coaching Calculator!H66',
    ProgramTier.SPARK_I:    'Coaching Calculator!H82',
    ProgramTier.SPARK_II:   'Coaching Calculator!H100',
    ProgramTier.AIIR_VISTA: 'Coaching Calculator!H118',
}

# SessionHours field → cell key mapping
_HOURS_FIELD_TO_KEY = {
    'coaching_zone_months':        'cz_months',
    'stakeholder_sessions_hours':  'stakeholder',
    'developmental_history_hours': 'dev_history',
    'threesixty_interview_hours':  'threesixty',
    'assessment_feedback_hours':   'assessment',
    'dev_planning_hours':          'dev_planning',
    'implementation_sessions':     'impl_sessions',
}


def _build_calculator_updates(pricing) -> list:
    """Build the batch_update list for the per-engagement calculator sheet."""
    updates = [
        {'range': 'Coaching Calculator!B15', 'values': [[pricing.bill_rate_per_hour]]},
        {'range': 'Coaching Calculator!B16', 'values': [[0.65]]},  # correct margin (template default 0.70 is wrong)
    ]

    tier_cells = _TIER_INPUT_CELLS.get(pricing.tier, {})
    hours = pricing.session_hours

    for field, key in _HOURS_FIELD_TO_KEY.items():
        if key in tier_cells:
            updates.append({
                'range': tier_cells[key],
                'values': [[getattr(hours, field)]],
            })

    return updates


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
    3. Calculate pricing inputs using business logic
    4. Generate engagement ID
    5. Copy calculator template, write all input cells, read total back from sheet
    6. Write to Tracker sheet using the sheet-sourced total
    7. Generate pricing rationale
    8. Save rationale to Drive
    9. Update Tracker with document URLs
    10. Get row number
    11. Generate email HTML for notification
    12. Return engagement data + email data

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

        # Initialize services
        google_manager = GoogleServicesManager(config)
        drive = GoogleDriveService(google_manager.get_drive_service())
        sheets = GoogleSheetsService(google_manager.get_sheets_service())
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
        # Step 3: Calculate pricing inputs
        # ====================
        logger.info("Step 3: Calculating pricing inputs with business logic")
        pricing = calculate_pricing(extracted)
        logger.info(f"Pricing inputs calculated:")
        logger.info(f"  - Tier: {pricing.tier.value}")
        logger.info(f"  - Bill Rate: ${pricing.bill_rate_per_hour}/hr")
        logger.info(f"  - Total Hours: {pricing.total_coaching_hours}")
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
        # Step 5: Write to Calculator sheet + read total back
        # ====================
        logger.info("Step 5: Creating per-engagement Calculator sheet and reading total")

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
        logger.info(f"✓ Created Calculator sheet: {calculator_url}")

        # Write all input cells for this tier
        calculator_updates = _build_calculator_updates(pricing)
        sheets.batch_update(per_engagement_sheet_id, calculator_updates)
        logger.info(f"✓ Wrote {len(calculator_updates)} input cells to Calculator")

        # Read the total back from the sheet — sheet formulas are the source of truth
        total_cell = _TIER_TOTAL_CELL.get(pricing.tier)
        sheet_total = 0.0
        if total_cell:
            try:
                result = sheets.read_range(per_engagement_sheet_id, total_cell)
                if result and result[0]:
                    sheet_total = float(str(result[0][0]).replace(',', ''))
                    logger.info(f"✓ Read total from sheet ({total_cell}): ${sheet_total:,.0f}")
                else:
                    logger.warning(f"Sheet returned empty for {total_cell} — total will be $0")
            except Exception as read_err:
                logger.warning(f"Could not read total from sheet: {read_err}")
        else:
            logger.warning(f"No total cell defined for tier {pricing.tier.value}")

        # Propagate sheet total so rationale and email use the correct value
        pricing.total_engagement_price = sheet_total
        pricing.price_per_participant = sheet_total

        # ====================
        # Step 6: Write to Tracker sheet
        # ====================
        logger.info("Step 6: Writing engagement to Tracker sheet")

        # Tracker columns (SIMPLIFIED DESIGN):
        # A: Engagement ID  B: Date Created  C: Client      D: Coachee     E: Title
        # F: Program        G: Duration      H: Total Price  I: Payment Terms
        # J: Calculator     K: SOW           L: Status       M: Notes
        # N-T: (empty)      U: Pricing Model Status

        tracker_row = [
            engagement_id,                                          # A
            datetime.now().strftime("%Y-%m-%d"),                    # B
            extracted.client_company_name,                          # C
            extracted.coachee_name,                                 # D
            extracted.coachee_title,                                # E
            pricing.tier.value,                                     # F
            f"{extracted.engagement_duration_months or ''} months", # G
            f"${sheet_total:,.0f}",                                 # H - Total Price (from sheet)
            pricing.payment_terms,                                  # I
            '',  # Calculator URL (updated in step 9)               # J
            '',  # SOW URL (populated by workflow 2)                # K
            'Pending Review',                                       # L
            '',                                                     # M
            '', '', '', '', '', '', '',                             # N-T
            'Pending Review',                                       # U
        ]

        sheets.append_row(
            config.tracker_sheet_id,
            f"{config.tracker_tab_name}!A:U",
            tracker_row
        )
        logger.info(f"✓ Added engagement to Tracker with Total Price=${sheet_total:,.0f}")

        # ====================
        # Step 7: Generate pricing rationale
        # ====================
        logger.info("Step 7: Generating pricing rationale")
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
        logger.info("Step 9: Updating Tracker with Calculator URL")
        sheets.update_row_by_engagement_id(
            config.tracker_sheet_id,
            config.tracker_tab_name,
            engagement_id,
            {
                'J': calculator_url,  # Column J: Calculator URL
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

        with open('templates/pricing_model_ready_email.html', 'r', encoding='utf-8') as f:
            email_template = Template(f.read())

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
            total_price=f"{sheet_total:,.0f}",
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
        logger.info(f"Total Price: ${sheet_total:,.0f}  (sourced from calculator sheet)")
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
                'total_price': sheet_total,
                'total_hours': pricing.total_coaching_hours,
                'bill_rate': pricing.bill_rate_per_hour
            }
        }

    except Exception as e:
        logger.error(f"ERROR in simplified workflow: {e}", exc_info=True)
        raise
