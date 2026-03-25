"""
Cron endpoint to watch for new transcripts
Runs every 5 minutes via Vercel cron job

UPDATED TO USE SIMPLIFIED WORKFLOW (NO EMAILS)
"""

from fastapi import APIRouter, HTTPException
from app.workflows.workflow_1_pricing_simplified import process_transcript_to_pricing_simplified
from app.services import GoogleDriveService, RedisService
from app.config import get_config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/cron/watch-transcripts")
async def watch_transcripts_cron():
    """
    Check for new transcripts in the Transcripts folder

    This endpoint is called every 5 minutes by Vercel cron.

    Process:
    1. List files in Transcripts folder
    2. Filter to .txt files only
    3. Check Redis to skip already-processed files
    4. For each new file:
       - Mark as processing in Redis
       - Trigger Workflow 1
       - Mark as completed in Redis

    Returns:
        Status dict with processing results
    """
    try:
        config = get_config()
        logger.info("Cron job triggered: Checking for new transcripts")

        # Initialize services
        drive = GoogleDriveService(config.google_credentials_path)
        redis = RedisService(config.upstash_redis_rest_url, config.upstash_redis_rest_token)

        # Step 1: List files in Transcripts folder
        files = drive.list_files_in_folder(
            config.transcripts_folder_id,
            mime_type='text/plain',  # Only .txt files
            order_by='createdTime desc'
        )

        logger.info(f"Found {len(files)} transcript files")

        processed_count = 0
        skipped_count = 0
        errors = []

        # Step 2: Process each new file
        for file in files:
            file_id = file['id']
            filename = file['name']

            # Check if already processed
            if redis.is_already_processed(file_id):
                logger.info(f"Skipping already-processed file: {filename}")
                skipped_count += 1
                continue

            try:
                logger.info(f"Processing new transcript: {filename}")

                # Mark as processing
                redis.track_processing(file_id, 'processing', ttl=3600)

                # Trigger Workflow 1 (SIMPLIFIED - NO EMAILS)
                engagement_id = await process_transcript_to_pricing_simplified(
                    file_id,
                    filename,
                    config
                )

                # Mark as completed
                redis.track_processing(file_id, 'completed', ttl=86400)

                processed_count += 1
                logger.info(f"Successfully processed {filename} → {engagement_id}")

            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                errors.append({
                    'file': filename,
                    'error': str(e)
                })

                # Mark as failed
                redis.track_processing(file_id, 'failed', ttl=3600)

        # Return summary
        result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_files': len(files),
            'processed': processed_count,
            'skipped': skipped_count,
            'errors': len(errors),
            'error_details': errors if errors else None
        }

        logger.info(f"Cron job completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in cron job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
