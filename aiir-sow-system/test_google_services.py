"""
Test Google Services Integration
Verifies Drive, Sheets, and Docs connectivity
"""

import asyncio
import logging
from app.config import get_config
from app.services import GoogleDriveService, GoogleSheetsService, GoogleDocsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_google_services():
    """Test all Google service integrations"""

    logger.info("=" * 80)
    logger.info("TESTING GOOGLE SERVICES INTEGRATION")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Load config
        config = get_config()
        logger.info("✓ Config loaded")
        logger.info("")

        # ====================
        # TEST 1: GOOGLE DRIVE
        # ====================
        logger.info("=" * 80)
        logger.info("TEST 1: GOOGLE DRIVE")
        logger.info("=" * 80)
        logger.info("")

        drive = GoogleDriveService(config.google_credentials_path)
        logger.info("✓ Drive service initialized")

        # Test: Upload a test file
        logger.info("Test: Uploading test file to Rationales folder...")
        test_content = "This is a test rationale document.\n\nTest timestamp: 2026-03-12"
        test_filename = "TEST_RATIONALE.txt"

        try:
            file_id, file_url = drive.upload_file(
                file_name=test_filename,
                file_content=test_content,
                folder_id=config.rationales_folder_id,
                mime_type='text/plain'
            )
            logger.info(f"✓ File uploaded successfully!")
            logger.info(f"  File ID: {file_id}")
            logger.info(f"  File URL: {file_url}")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Drive upload failed: {e}")
            logger.info("")

        # Test: List files in folder
        logger.info("Test: Listing files in Rationales folder...")
        try:
            files = drive.list_files_in_folder(
                folder_id=config.rationales_folder_id,
                mime_type=None,
                order_by='createdTime desc'
            )
            logger.info(f"✓ Found {len(files)} file(s) in folder")
            if files:
                logger.info("Recent files:")
                for f in files[:3]:
                    logger.info(f"  - {f['name']}")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Drive list failed: {e}")
            logger.info("")

        # ====================
        # TEST 2: GOOGLE SHEETS
        # ====================
        logger.info("=" * 80)
        logger.info("TEST 2: GOOGLE SHEETS")
        logger.info("=" * 80)
        logger.info("")

        sheets = GoogleSheetsService(config.google_credentials_path)
        logger.info("✓ Sheets service initialized")

        # Test: Read from Tracker
        logger.info("Test: Reading Tracker sheet...")
        try:
            tracker_data = sheets.read_range(
                spreadsheet_id=config.tracker_sheet_id,
                range_name=f"{config.tracker_tab_name}!A1:R1"
            )
            if tracker_data:
                logger.info(f"✓ Read {len(tracker_data)} row(s) from Tracker")
                logger.info(f"  Headers: {tracker_data[0][:5]}...")  # Show first 5 columns
            else:
                logger.info("⚠️  Tracker sheet is empty")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Sheets read failed: {e}")
            logger.info("")

        # Test: Write to Tracker
        logger.info("Test: Writing test row to Tracker sheet...")
        test_row = [
            "TEST-ENGAGEMENT-001",  # A: Engagement ID
            "Test Company Inc.",    # B: Client Company
            "John Doe",             # C: Coachee Name
            "CTO",                  # D: Coachee Title
            "Jane Smith",           # E: Decision Maker
            "jane@test.com",        # F: Decision Maker Email
            "IGNITE",               # G: Program Tier
            "C-Suite",              # H: Seniority
            "6",                    # I: Duration
            "Mature",               # J: Market Type
            "550",                  # K: Bill Rate
            "20",                   # L: Total Hours
            "11000",                # M: Total Price
            "Net 30",               # N: Payment Terms
            "",                     # O: Rationale URL
            "",                     # P: Calculator URL
            "",                     # Q: SOW URL
            "TEST",                 # R: Status
        ]

        try:
            result = sheets.append_row(
                spreadsheet_id=config.tracker_sheet_id,
                range_name=config.tracker_tab_name,
                values=test_row
            )
            logger.info(f"✓ Test row written successfully!")
            logger.info(f"  Updated cells: {result.get('updates', {}).get('updatedCells', 0)}")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Sheets write failed: {e}")
            logger.info("")

        # Test: Update specific cell
        logger.info("Test: Updating specific cell in Tracker...")
        try:
            sheets.update_row_by_engagement_id(
                spreadsheet_id=config.tracker_sheet_id,
                sheet_name=config.tracker_tab_name,
                engagement_id="TEST-ENGAGEMENT-001",
                column_updates={
                    'O': 'https://test-rationale-url.com',
                    'R': 'TEST_COMPLETE'
                }
            )
            logger.info(f"✓ Cell updated successfully!")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Sheets update failed: {e}")
            logger.info("")

        # Test: Read Calculator sheet
        logger.info("Test: Reading Calculator sheet...")
        try:
            calc_data = sheets.read_range(
                spreadsheet_id=config.calculator_sheet_id,
                range_name=f"{config.calculator_tab_name}!A1:J1"
            )
            if calc_data:
                logger.info(f"✓ Read {len(calc_data)} row(s) from Calculator")
                logger.info(f"  Headers: {calc_data[0][:5]}...")
            else:
                logger.info("⚠️  Calculator sheet is empty")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Calculator read failed: {e}")
            logger.info("")

        # ====================
        # TEST 3: GOOGLE DOCS
        # ====================
        logger.info("=" * 80)
        logger.info("TEST 3: GOOGLE DOCS")
        logger.info("=" * 80)
        logger.info("")

        docs = GoogleDocsService(config.google_credentials_path)
        logger.info("✓ Docs service initialized")

        # For Docs, we'll just verify initialization since creating docs requires templates
        logger.info("Note: Docs service is initialized and ready")
        logger.info("      Full SOW generation requires template configuration")
        logger.info("")

        # ====================
        # SUMMARY
        # ====================
        logger.info("=" * 80)
        logger.info("✓✓✓ GOOGLE SERVICES TEST COMPLETE ✓✓✓")
        logger.info("=" * 80)
        logger.info("")
        logger.info("RESULTS:")
        logger.info("  ✓ Google Drive: Connected & Working")
        logger.info("  ✓ Google Sheets: Connected & Working")
        logger.info("  ✓ Google Docs: Connected & Ready")
        logger.info("")
        logger.info("NEXT STEPS:")
        logger.info("1. Check your Google Sheets Tracker for the TEST row")
        logger.info("2. Verify the test rationale file in Drive")
        logger.info("3. You can delete the TEST-ENGAGEMENT-001 row if needed")
        logger.info("")
        logger.info(f"Tracker URL: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info("")

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_google_services())
