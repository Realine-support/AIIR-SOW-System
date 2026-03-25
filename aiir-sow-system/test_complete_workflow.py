"""
Test Complete Workflow with Template Duplication
Tests: Transcript → Calculator + SOW + Tracker
"""

import asyncio
import logging
from app.config import get_config
from app.services import GoogleDriveService
from app.workflows.workflow_complete_with_templates import process_transcript_complete

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_complete_workflow():
    """Test the complete workflow with template duplication"""

    logger.info("=" * 80)
    logger.info("TESTING COMPLETE WORKFLOW WITH TEMPLATES")
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

        # Get transcript from Drive
        logger.info("Finding transcript in folder...")
        files = drive.list_files_in_folder(
            config.transcripts_folder_id,
            mime_type=None,
            order_by='createdTime desc'
        )

        txt_files = [f for f in files if f['name'].endswith('.txt')]

        if not txt_files:
            logger.error("❌ No transcript files found!")
            return

        # Use most recent transcript
        transcript_file = txt_files[0]
        file_id = transcript_file['id']
        filename = transcript_file['name']

        logger.info(f"✓ Found transcript: {filename}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("STARTING COMPLETE WORKFLOW")
        logger.info("=" * 80)
        logger.info("")

        # Run the complete workflow
        engagement_id = await process_transcript_complete(
            file_id=file_id,
            filename=filename,
            config=config
        )

        logger.info("")
        logger.info("=" * 80)
        logger.info("✓✓✓ TEST COMPLETE ✓✓✓")
        logger.info("=" * 80)
        logger.info(f"Engagement ID: {engagement_id}")
        logger.info("")
        logger.info("CHECK YOUR RESULTS:")
        logger.info(f"1. Tracker Sheet: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
        logger.info(f"2. Client Folder: https://drive.google.com/drive/folders/{config.client_master_folder_id}")
        logger.info("")
        logger.info("You should see:")
        logger.info("  ✓ New row in Tracker with all links")
        logger.info("  ✓ Calculator spreadsheet (duplicated from template)")
        logger.info("  ✓ SOW document (duplicated from template)")
        logger.info("  ✓ Status: 🟡 Pending Review")
        logger.info("")
        logger.info("Next: Update Status to 'Approved' or 'Rejected' in Tracker")
        logger.info("=" * 80)

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
