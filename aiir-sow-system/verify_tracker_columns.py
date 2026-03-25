"""
Verify Tracker Sheet column structure
"""

from app.services import GoogleSheetsService
from app.config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)

logger.info("=" * 80)
logger.info("TRACKER SHEET COLUMN VERIFICATION")
logger.info("=" * 80)

# Read headers
headers_range = f"{config.tracker_tab_name}!A1:Z1"
headers = sheets.read_range(config.tracker_sheet_id, headers_range)

if headers:
    headers_list = headers[0]
    logger.info(f"\nTotal columns: {len(headers_list)}")
    logger.info("\nColumn mapping:")

    expected_columns = {
        0: 'A - Engagement ID',
        1: 'B - Client Company',
        2: 'C - Coachee Name',
        3: 'D - Coachee Title',
        4: 'E - Decision Maker Name',
        5: 'F - Decision Maker Email',
        6: 'G - Program Tier',
        7: 'H - Seniority Level',
        8: 'I - Duration (months)',
        9: 'J - Market Type',
        10: 'K - Bill Rate',
        11: 'L - Total Hours',
        12: 'M - Total Price',
        13: 'N - Payment Terms',
        14: 'O - Rationale URL',
        15: 'P - Calculator URL',
        16: 'Q - SOW URL',
        17: 'R - Status',
        18: 'S - Created At',
        19: 'T - Updated At',
        20: 'U - Pricing Model Status'
    }

    for i, header in enumerate(headers_list):
        col_letter = chr(65 + i)  # A=65
        expected = expected_columns.get(i, 'Unknown')
        status = "✓" if i in expected_columns else "?"
        logger.info(f"  {status} Column {col_letter} (index {i}): '{header}'")
        if i in expected_columns:
            logger.info(f"      Expected: {expected}")

    logger.info("\n" + "=" * 80)
    logger.info("KEY COLUMNS FOR WORKFLOWS:")
    logger.info("=" * 80)

    logger.info("\nWorkflow 1 (Pricing Model Generation):")
    logger.info(f"  - Column O (index 14): {headers_list[14] if len(headers_list) > 14 else 'MISSING'} - Rationale URL")
    logger.info(f"  - Column P (index 15): {headers_list[15] if len(headers_list) > 15 else 'MISSING'} - Calculator URL")
    logger.info(f"  - Column Q (index 16): {headers_list[16] if len(headers_list) > 16 else 'MISSING'} - SOW URL (empty initially)")
    logger.info(f"  - Column R (index 17): {headers_list[17] if len(headers_list) > 17 else 'MISSING'} - Status")
    logger.info(f"  - Column U (index 20): {headers_list[20] if len(headers_list) > 20 else 'MISSING'} - Pricing Model Status")

    logger.info("\nWorkflow 2 (SOW Generation - triggers on Column U = 'Approved'):")
    logger.info(f"  - Column Q (index 16): {headers_list[16] if len(headers_list) > 16 else 'MISSING'} - SOW URL (will be filled)")
    logger.info(f"  - Column R (index 17): {headers_list[17] if len(headers_list) > 17 else 'MISSING'} - Status (will change to 'SOW Generated')")

    # Check if all required columns exist
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION RESULTS:")
    logger.info("=" * 80)

    all_good = True

    if len(headers_list) < 21:
        logger.error("❌ ERROR: Not enough columns! Expected at least 21 columns (A-U)")
        all_good = False
    else:
        logger.info("✓ Column count correct: 21+ columns")

    if len(headers_list) > 20 and headers_list[20] == "Pricing Model Status":
        logger.info("✓ Column U exists: 'Pricing Model Status'")
    else:
        logger.error("❌ ERROR: Column U missing or incorrect!")
        all_good = False

    if len(headers_list) > 16:
        logger.info(f"✓ Column Q exists: '{headers_list[16]}' (for SOW URL)")
    else:
        logger.error("❌ ERROR: Column Q missing!")
        all_good = False

    if all_good:
        logger.info("\n" + "=" * 80)
        logger.info("✓✓✓ ALL CHECKS PASSED ✓✓✓")
        logger.info("=" * 80)
        logger.info("\nThe tracking sheet is correctly configured!")
        logger.info("\nWorkflow logic:")
        logger.info("  1. Transcript uploaded → Pricing model created")
        logger.info("  2. Row added with Column Q (SOW URL) = EMPTY")
        logger.info("  3. Column U (Pricing Model Status) = 'Pending Review'")
        logger.info("  4. User changes Column U to 'Approved'")
        logger.info("  5. n8n triggers Workflow 2")
        logger.info("  6. SOW generated → Column Q filled with SOW link")
        logger.info("  7. Column R updated to 'SOW Generated'")
    else:
        logger.error("\n❌ ERRORS FOUND - Please fix before proceeding")

    logger.info("\n" + "=" * 80)

else:
    logger.error("Could not read headers from Tracker sheet!")
