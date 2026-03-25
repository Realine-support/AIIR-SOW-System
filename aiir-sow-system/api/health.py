"""
Health check endpoints with dependency verification
Verifies connectivity to all external services
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


async def check_openai_connectivity(api_key: str) -> Dict[str, Any]:
    """Test OpenAI API connectivity"""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        # Simple API call to verify connectivity
        # Using a minimal request to avoid costs
        response = client.models.list()

        return {
            "status": "healthy",
            "message": "OpenAI API accessible",
            "models_available": len(list(response.data)) > 0
        }
    except Exception as e:
        logger.error(f"OpenAI health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"OpenAI API error: {str(e)}"
        }


async def check_google_apis_connectivity(config) -> Dict[str, Any]:
    """Test Google APIs connectivity (Drive, Sheets, Docs)"""
    try:
        from app.services.google_services import GoogleServicesManager

        # Initialize Google services
        google_manager = GoogleServicesManager(config)

        # Test Drive API by listing shared drive
        try:
            drive_service = google_manager.get_drive_service()
            drive_response = drive_service.files().list(
                corpora='drive',
                driveId=config.shared_drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageSize=1
            ).execute()
            drive_ok = True
        except Exception as e:
            logger.error(f"Google Drive check failed: {str(e)}")
            drive_ok = False

        # Test Sheets API by getting tracker sheet metadata
        try:
            sheets_service = google_manager.get_sheets_service()
            sheets_response = sheets_service.spreadsheets().get(
                spreadsheetId=config.tracker_sheet_id
            ).execute()
            sheets_ok = True
        except Exception as e:
            logger.error(f"Google Sheets check failed: {str(e)}")
            sheets_ok = False

        # Test Docs API
        try:
            docs_service = google_manager.get_docs_service()
            docs_ok = docs_service is not None
        except Exception as e:
            logger.error(f"Google Docs check failed: {str(e)}")
            docs_ok = False

        all_healthy = drive_ok and sheets_ok and docs_ok

        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "message": "Google APIs accessible" if all_healthy else "Some Google APIs failed",
            "services": {
                "drive": "healthy" if drive_ok else "unhealthy",
                "sheets": "healthy" if sheets_ok else "unhealthy",
                "docs": "healthy" if docs_ok else "unhealthy"
            }
        }
    except Exception as e:
        logger.error(f"Google APIs health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Google APIs error: {str(e)}",
            "services": {
                "drive": "unknown",
                "sheets": "unknown",
                "docs": "unknown"
            }
        }


# Redis health check removed - Redis is not used in this system
# async def check_redis_connectivity(redis_url: str, redis_token: str) -> Dict[str, Any]:
#     """Test Upstash Redis connectivity"""
#     pass


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Comprehensive health check with dependency verification
    Tests connectivity to:
    - OpenAI API
    - Google Drive API
    - Google Sheets API
    - Google Docs API
    """
    from app.config import get_config

    config = get_config()

    # Run all health checks in parallel (Redis removed)
    openai_check, google_check = await asyncio.gather(
        check_openai_connectivity(config.openai_api_key),
        check_google_apis_connectivity(config),
        return_exceptions=True
    )

    # Handle exceptions from gather
    if isinstance(openai_check, Exception):
        openai_check = {"status": "unhealthy", "message": str(openai_check)}
    if isinstance(google_check, Exception):
        google_check = {"status": "unhealthy", "message": str(google_check)}

    # Determine overall health (Redis check removed)
    all_healthy = (
        openai_check.get("status") == "healthy" and
        google_check.get("status") == "healthy"
    )

    response = {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": config.environment,
        "version": "1.0.0",
        "dependencies": {
            "openai": openai_check,
            "google_apis": google_check
        },
        "endpoints": {
            "google_drive_trigger": "/webhooks/google-drive-file-added",
            "pricing_model_approved": "/webhooks/pricing-model-approved"
        }
    }

    # Return 503 if any dependency is unhealthy
    if not all_healthy:
        raise HTTPException(status_code=503, detail=response)

    return response


@router.get("/health/live")
async def liveness_check():
    """
    Simple liveness probe for Railway/Kubernetes
    Returns 200 if the application is running
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe - checks if app can serve traffic
    Performs quick checks on critical dependencies
    """
    from app.config import get_config

    try:
        config = get_config()

        # Quick validation that critical config is loaded (Redis check removed)
        assert config.openai_api_key, "OpenAI API key not configured"
        assert config.tracker_sheet_id, "Tracker sheet ID not configured"

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": config.environment
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
