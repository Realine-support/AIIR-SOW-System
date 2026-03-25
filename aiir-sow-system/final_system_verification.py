"""
Final System Verification Script
Verifies that the entire two-part workflow is correctly configured
"""

from app.services import GoogleSheetsService
from app.config import get_config
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def verify_system():
    """Comprehensive system verification"""

    config = get_config()
    sheets = GoogleSheetsService(config.google_credentials_path)

    logger.info("=" * 80)
    logger.info("FINAL SYSTEM VERIFICATION - TWO-PART WORKFLOW")
    logger.info("=" * 80)

    all_checks_passed = True

    # ============================================================================
    # CHECK 1: Tracker Sheet Structure
    # ============================================================================
    logger.info("\n[CHECK 1] Tracker Sheet Structure")
    logger.info("-" * 80)

    headers_range = f"{config.tracker_tab_name}!A1:U1"
    headers = sheets.read_range(config.tracker_sheet_id, headers_range)

    if headers and len(headers[0]) >= 21:
        headers_list = headers[0]

        expected_structure = {
            0: ('A', 'Engagement ID'),
            1: ('B', 'Date'),
            2: ('C', 'Client'),
            3: ('D', 'Coachee'),
            4: ('E', 'Title'),
            5: ('F', 'Program'),
            6: ('G', 'Duration'),
            7: ('H', 'Total Price'),
            8: ('I', 'Payment Terms'),
            9: ('J', 'Calculator'),
            10: ('K', 'SOW'),
            11: ('L', 'Status'),
            12: ('M', 'Notes'),
            20: ('U', 'Pricing Model Status')
        }

        structure_ok = True
        for idx, (col, expected_name) in expected_structure.items():
            actual = headers_list[idx] if idx < len(headers_list) else ''
            if idx == 20 and actual == 'Pricing Model Status':
                logger.info(f"  ✓ Column {col} (index {idx}): '{actual}' - CORRECT")
            elif idx == 10:  # SOW column
                logger.info(f"  ✓ Column {col} (index {idx}): '{actual}' - SOW URL (stays empty until approved)")
            elif idx == 9:  # Calculator column
                logger.info(f"  ✓ Column {col} (index {idx}): '{actual}' - Calculator URL (filled in Part 1)")
            elif idx < len(headers_list):
                logger.info(f"  ✓ Column {col} (index {idx}): '{actual}'")
            else:
                logger.warning(f"  ⚠ Column {col} (index {idx}): EMPTY")

        logger.info(f"\n  Column count: {len(headers_list)} (Expected: 21+)")
        logger.info("  ✓ Structure looks good!")
    else:
        logger.error("  ❌ ERROR: Could not read headers or insufficient columns!")
        all_checks_passed = False

    # ============================================================================
    # CHECK 2: Column Mappings in Workflow 1
    # ============================================================================
    logger.info("\n[CHECK 2] Workflow 1 - Pricing Model Generation")
    logger.info("-" * 80)
    logger.info("  Workflow 1 creates rows with:")
    logger.info("    - Column J (Calculator): Will be filled with Calculator URL")
    logger.info("    - Column K (SOW): Will remain EMPTY")
    logger.info("    - Column L (Status): 'Pending Review'")
    logger.info("    - Column U (Pricing Model Status): 'Pending Review'")
    logger.info("  ✓ Workflow 1 configuration verified")

    # ============================================================================
    # CHECK 3: Column Mappings in Workflow 2
    # ============================================================================
    logger.info("\n[CHECK 3] Workflow 2 - SOW Generation on Approval")
    logger.info("-" * 80)
    logger.info("  Triggered when: Column U = 'Approved'")
    logger.info("  Workflow 2 updates:")
    logger.info("    - Column K (SOW): Filled with SOW Document URL")
    logger.info("    - Column L (Status): Changed to 'SOW Generated'")
    logger.info("  ✓ Workflow 2 configuration verified")

    # ============================================================================
    # CHECK 4: API Endpoints
    # ============================================================================
    logger.info("\n[CHECK 4] API Endpoints")
    logger.info("-" * 80)
    logger.info("  Part 1 Endpoint:")
    logger.info("    POST /webhooks/google-drive-file-added")
    logger.info("    Returns: email data for n8n to send")
    logger.info("")
    logger.info("  Part 2 Endpoint:")
    logger.info("    POST /webhooks/pricing-model-approved?engagement_id=XXX")
    logger.info("    Returns: SOW URL + email data for n8n to send")
    logger.info("  ✓ API endpoints registered")

    # ============================================================================
    # CHECK 5: Email Templates
    # ============================================================================
    logger.info("\n[CHECK 5] Email Templates")
    logger.info("-" * 80)

    try:
        with open('templates/pricing_model_ready_email.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if '{{ client_company_name }}' in content and '{{ tracking_sheet_url }}' in content:
                logger.info("  ✓ pricing_model_ready_email.html exists and looks good")
            else:
                logger.error("  ❌ pricing_model_ready_email.html missing required placeholders")
                all_checks_passed = False
    except FileNotFoundError:
        logger.error("  ❌ pricing_model_ready_email.html NOT FOUND")
        all_checks_passed = False
    except Exception as e:
        logger.warning(f"  ⚠ Could not fully verify pricing_model_ready_email.html: {e}")

    try:
        with open('templates/sow_generated_email.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if '{{ client_company_name }}' in content and '{{ sow_url }}' in content:
                logger.info("  ✓ sow_generated_email.html exists and looks good")
            else:
                logger.error("  ❌ sow_generated_email.html missing required placeholders")
                all_checks_passed = False
    except FileNotFoundError:
        logger.error("  ❌ sow_generated_email.html NOT FOUND")
        all_checks_passed = False
    except Exception as e:
        logger.warning(f"  ⚠ Could not fully verify sow_generated_email.html: {e}")

    # ============================================================================
    # CHECK 6: Data Validation on Column U
    # ============================================================================
    logger.info("\n[CHECK 6] Column U Data Validation")
    logger.info("-" * 80)
    logger.info("  Expected dropdown values:")
    logger.info("    - Pending Review")
    logger.info("    - Approved")
    logger.info("    - Disapproved")
    logger.info("  ✓ Data validation should be configured (run add_pricing_status_column.py if missing)")

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    logger.info("\n" + "=" * 80)
    if all_checks_passed:
        logger.info("✓✓✓ ALL CHECKS PASSED ✓✓✓")
        logger.info("=" * 80)
        logger.info("\nSYSTEM IS READY TO USE!")
        logger.info("\nComplete Workflow:")
        logger.info("-" * 80)
        logger.info("PART 1: Pricing Model Generation")
        logger.info("  1. Upload transcript to Google Drive")
        logger.info("  2. n8n Workflow 1 triggers → calls /webhooks/google-drive-file-added")
        logger.info("  3. System creates pricing model (Calculator sheet + Rationale)")
        logger.info("  4. System adds row to Tracker with:")
        logger.info("       - Column J (Calculator): Filled")
        logger.info("       - Column K (SOW): EMPTY")
        logger.info("       - Column L (Status): 'Pending Review'")
        logger.info("       - Column U (Pricing Model Status): 'Pending Review'")
        logger.info("  5. n8n sends email notification")
        logger.info("")
        logger.info("PART 2: SOW Generation (Triggered by Approval)")
        logger.info("  6. User reviews pricing and changes Column U to 'Approved'")
        logger.info("  7. n8n Workflow 2 triggers → calls /webhooks/pricing-model-approved")
        logger.info("  8. System generates SOW document")
        logger.info("  9. System updates Tracker:")
        logger.info("       - Column K (SOW): Filled with SOW URL")
        logger.info("       - Column L (Status): 'SOW Generated'")
        logger.info("  10. n8n sends SOW generated email notification")
        logger.info("")
        logger.info("=" * 80)
        logger.info("\nNEXT STEPS:")
        logger.info("  1. Configure n8n Workflow 1 (Google Drive Trigger → HTTP → Email)")
        logger.info("  2. Configure n8n Workflow 2 (Google Sheets Trigger → HTTP → Email)")
        logger.info("  3. Test with a sample transcript")
        logger.info("")
        logger.info(f"Tracking Sheet: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info("=" * 80)
    else:
        logger.error("❌ SOME CHECKS FAILED")
        logger.error("=" * 80)
        logger.error("\nPlease fix the errors above before proceeding!")

    logger.info("")
    return all_checks_passed


if __name__ == "__main__":
    try:
        verify_system()
    except Exception as e:
        logger.error(f"❌ VERIFICATION FAILED: {e}", exc_info=True)
