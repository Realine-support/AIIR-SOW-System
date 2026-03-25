"""
Test script for simplified workflow
Tests transcript processing, pricing calculation, and Google Sheets updates
"""

import asyncio
import logging
from app.config import get_config
from app.workflows.workflow_1_pricing_simplified import process_transcript_to_pricing_simplified
from app.services import GoogleDriveService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_workflow():
    """Test the simplified workflow with a real or sample transcript"""

    logger.info("=" * 80)
    logger.info("TESTING SIMPLIFIED WORKFLOW (NO EMAILS)")
    logger.info("=" * 80)

    try:
        # Load config
        config = get_config()
        logger.info("✓ Config loaded")

        # Initialize Drive service
        drive = GoogleDriveService(config.google_credentials_path)
        logger.info("✓ Drive service initialized")

        # List transcripts in the folder
        logger.info(f"Checking transcripts folder: {config.transcripts_folder_id}")

        # First check all files (no MIME filter) to debug
        logger.info("Checking all files in folder...")
        all_files = drive.list_files_in_folder(
            config.transcripts_folder_id,
            mime_type=None,
            order_by='createdTime desc'
        )

        logger.info(f"Total files found (all types): {len(all_files)}")
        if all_files:
            logger.info("Files in folder:")
            for f in all_files[:10]:
                logger.info(f"  - {f['name']} (MIME: {f.get('mimeType', 'unknown')})")
        logger.info("")

        # Now filter for text files
        files = [f for f in all_files if f['name'].endswith('.txt') or f.get('mimeType') == 'text/plain']

        if not files:
            logger.error("❌ No .txt transcript files found in the Transcripts folder!")
            logger.info("")
            logger.info("To test:")
            logger.info("1. Upload a .txt transcript to Google Drive")
            logger.info(f"2. Move it to folder ID: {config.transcripts_folder_id}")
            logger.info("3. Run this test script again")
            logger.info("")
            if all_files:
                logger.info("Note: Found other files in the folder, but none are .txt files")
            return

        logger.info(f"✓ Found {len(files)} transcript file(s)")
        logger.info("")

        # Show available files
        logger.info("Available transcripts:")
        for i, file in enumerate(files[:5], 1):  # Show first 5
            logger.info(f"  {i}. {file['name']} (ID: {file['id']})")
        logger.info("")

        # Use the first/most recent file
        test_file = files[0]
        file_id = test_file['id']
        filename = test_file['name']

        logger.info(f"Testing with: {filename}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("STARTING WORKFLOW")
        logger.info("=" * 80)
        logger.info("")

        # Run the workflow
        engagement_id = await process_transcript_to_pricing_simplified(
            file_id=file_id,
            filename=filename,
            config=config
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("✓✓✓ TEST COMPLETED SUCCESSFULLY ✓✓✓")
        logger.info("=" * 80)
        logger.info(f"Engagement ID: {engagement_id}")
        logger.info("")
        logger.info("Check your Google Sheets Tracker to see the new row!")
        logger.info(f"Tracker URL: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info("")

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow())
