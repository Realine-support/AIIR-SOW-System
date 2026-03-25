"""
Redis Service for State Management
Uses Upstash Redis for serverless-friendly state tracking
"""

from typing import Optional, Dict, Any
import json
from upstash_redis import Redis
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """
    Redis service for state management

    Tracks:
    - Workflow states (pricing_review, sow_generation, etc.)
    - Pending approvals
    - Processing status
    """

    def __init__(self, redis_url: str, redis_token: str):
        """
        Initialize Redis service

        Args:
            redis_url: Upstash Redis REST URL
            redis_token: Upstash Redis token
        """
        self.redis = Redis(url=redis_url, token=redis_token)

    def set_state(
        self,
        engagement_id: str,
        state: str,
        data: Optional[Dict[str, Any]] = None,
        ttl: int = 86400  # 24 hours default
    ) -> None:
        """
        Set workflow state for an engagement

        Args:
            engagement_id: Unique engagement ID
            state: State name (e.g., 'pricing_review', 'sow_generation')
            data: Optional additional data to store
            ttl: Time to live in seconds (default 24 hours)
        """
        try:
            key = f"engagement:{engagement_id}:state"

            state_data = {
                'state': state,
                'data': data or {}
            }

            self.redis.setex(
                key,
                ttl,
                json.dumps(state_data)
            )

            logger.info(f"Set state for {engagement_id}: {state}")

        except Exception as e:
            logger.error(f"Error setting state for {engagement_id}: {e}")
            raise

    def get_state(self, engagement_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow state for an engagement

        Args:
            engagement_id: Engagement ID

        Returns:
            State data dict or None if not found
        """
        try:
            key = f"engagement:{engagement_id}:state"
            data = self.redis.get(key)

            if data:
                return json.loads(data)

            return None

        except Exception as e:
            logger.error(f"Error getting state for {engagement_id}: {e}")
            raise

    def delete_state(self, engagement_id: str) -> None:
        """
        Delete workflow state

        Args:
            engagement_id: Engagement ID
        """
        try:
            key = f"engagement:{engagement_id}:state"
            self.redis.delete(key)

            logger.info(f"Deleted state for {engagement_id}")

        except Exception as e:
            logger.error(f"Error deleting state for {engagement_id}: {e}")
            raise

    def list_pending_approvals(self, state: str) -> list[str]:
        """
        List all engagements in a specific state

        Args:
            state: State to filter by (e.g., 'pricing_review')

        Returns:
            List of engagement IDs
        """
        try:
            # Scan for all engagement keys
            cursor = 0
            matching_ids = []

            while True:
                cursor, keys = self.redis.scan(cursor, match="engagement:*:state")

                for key in keys:
                    data = self.redis.get(key)
                    if data:
                        state_data = json.loads(data)
                        if state_data.get('state') == state:
                            # Extract engagement ID from key
                            engagement_id = key.split(':')[1]
                            matching_ids.append(engagement_id)

                if cursor == 0:
                    break

            logger.info(f"Found {len(matching_ids)} engagements in state '{state}'")
            return matching_ids

        except Exception as e:
            logger.error(f"Error listing pending approvals: {e}")
            raise

    def track_processing(
        self,
        file_id: str,
        status: str,
        ttl: int = 3600  # 1 hour default
    ) -> None:
        """
        Track file processing status to avoid duplicates

        Args:
            file_id: Google Drive file ID
            status: Processing status (e.g., 'processing', 'completed', 'failed')
            ttl: Time to live in seconds
        """
        try:
            key = f"processing:{file_id}"
            self.redis.setex(key, ttl, status)

            logger.info(f"Tracking processing for file {file_id}: {status}")

        except Exception as e:
            logger.error(f"Error tracking processing: {e}")
            raise

    def is_already_processed(self, file_id: str) -> bool:
        """
        Check if a file has already been processed

        Args:
            file_id: Google Drive file ID

        Returns:
            True if already processed
        """
        try:
            key = f"processing:{file_id}"
            status = self.redis.get(key)

            return status is not None

        except Exception as e:
            logger.error(f"Error checking if processed: {e}")
            raise
