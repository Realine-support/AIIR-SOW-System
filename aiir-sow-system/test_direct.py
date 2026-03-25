"""
Direct test - uploads sample transcript and processes it
No need to manually upload to Drive first
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


async def test_direct():
    """Test by uploading sample transcript directly"""

    logger.info("=" * 80)
    logger.info("DIRECT TEST - UPLOADING & PROCESSING SAMPLE TRANSCRIPT")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Load config
        config = get_config()
        logger.info("✓ Config loaded")

        # Initialize Drive service
        drive = GoogleDriveService(config.google_credentials_path)
        logger.info("✓ Drive service initialized")
        logger.info("")

        # Read sample transcript
        logger.info("Reading sample transcript from local file...")
        with open('sample_transcript.txt', 'r', encoding='utf-8') as f:
            transcript_content = f.read()

        logger.info(f"✓ Loaded transcript: {len(transcript_content)} characters")
        logger.info("")

        # Upload to Drive
        logger.info("Uploading transcript to Google Drive...")
        filename = "sample_transcript_test.txt"
        file_id, file_url = drive.upload_file(
            file_name=filename,
            file_content=transcript_content,
            folder_id=config.transcripts_folder_id,
            mime_type='text/plain'
        )

        logger.info(f"✓ Uploaded to Drive")
        logger.info(f"  File ID: {file_id}")
        logger.info(f"  File URL: {file_url}")
        logger.info("")

        # Now process it
        logger.info("=" * 80)
        logger.info("STARTING WORKFLOW")
        logger.info("=" * 80)
        logger.info("")

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
    asyncio.run(test_direct())
