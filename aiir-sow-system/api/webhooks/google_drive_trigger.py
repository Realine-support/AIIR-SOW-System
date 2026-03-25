"""
Webhook endpoint for n8n Google Drive file trigger
Triggered when a new file is added to the SOW Templates folder
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from app.workflows.workflow_1_pricing_simplified import process_transcript_to_pricing_simplified
from app.services import GoogleDriveService, GoogleSheetsService
from app.config import get_config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class GoogleDriveFilePayload(BaseModel):
    """
    Expected payload from n8n Google Drive Trigger

    The Google Drive Trigger node sends file metadata when a new file is created
    """
    id: str = Field(..., description="Google Drive file ID")
    name: str = Field(..., description="File name")
    mimeType: Optional[str] = Field(None, description="MIME type of the file")
    webViewLink: Optional[str] = Field(None, description="Link to view file in Drive")
    webContentLink: Optional[str] = Field(None, description="Link to download file")
    createdTime: Optional[str] = Field(None, description="File creation timestamp")
    modifiedTime: Optional[str] = Field(None, description="Last modified timestamp")


@router.post("/webhooks/google-drive-file-added")
async def google_drive_file_added(request: Request):
    """
    Handle new file upload from n8n Google Drive Trigger

    Workflow:
    1. Receive file metadata from n8n
    2. Validate file type (should be .txt transcript or .docx)
    3. Trigger Workflow 1 (Pricing Simplified)
    4. Return success with SOW and Pricing Calculator URLs

    n8n Configuration:
    - Trigger: Google Drive Trigger (watches specific folder)
    - HTTP Request Node: POST to this endpoint
    - Method: POST
    - URL (local): http://localhost:8000/webhooks/google-drive-file-added
    - URL (ngrok): https://YOUR-NGROK-URL/webhooks/google-drive-file-added
    - Body: {{ $json }} (passes entire trigger payload)

    Returns:
        JSON response with status, engagement_id, and file URLs
    """
    try:
        config = get_config()

        # Parse request body
        body = await request.json()
        logger.info(f"Received Google Drive file trigger: {body}")

        # n8n can send data in different formats, handle both cases
        # Case 1: Direct payload from Google Drive Trigger
        # Case 2: Wrapped in additional structure

        # Try to extract file data
        file_data = None
        if isinstance(body, dict):
            # Check if it's wrapped (e.g., body has a 'data' or 'json' key)
            if 'data' in body:
                file_data = body['data']
            elif 'json' in body:
                file_data = body['json']
            elif 'id' in body and 'name' in body:
                # Direct payload
                file_data = body
            else:
                # Sometimes n8n sends the first item of an array
                logger.warning(f"Unexpected body structure: {body.keys()}")
                file_data = body

        if not file_data:
            raise HTTPException(
                status_code=400,
                detail="Could not extract file data from request body"
            )

        # Extract file metadata
        file_id = file_data.get('id')
        filename = file_data.get('name')
        mime_type = file_data.get('mimeType', 'unknown')

        if not file_id or not filename:
            logger.error(f"Missing file_id or filename in payload: {file_data}")
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: 'id' and 'name' are required"
            )

        logger.info(f"Processing file: {filename} (ID: {file_id}, MIME: {mime_type})")

        # Validate file type (optional - can process any file type)
        # Uncomment to enforce file type restrictions:
        # valid_types = ['text/plain', 'application/vnd.google-apps.document',
        #                'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        # if mime_type not in valid_types:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Invalid file type: {mime_type}. Expected text or document file."
        #     )

        # Trigger Workflow 1 (Pricing Simplified)
        # This will:
        # 1. Download the file
        # 2. Extract variables with OpenAI
        # 3. Calculate pricing
        # 4. Create engagement in Tracker
        # 5. Create Calculator sheet
        # 6. Generate rationale
        # 7. Generate email HTML
        # 8. Return comprehensive data including email
        workflow_result = await process_transcript_to_pricing_simplified(
            file_id=file_id,
            filename=filename,
            config=config
        )

        engagement_id = workflow_result['engagement_id']
        logger.info(f"Successfully processed file {filename} → Engagement: {engagement_id}")

        # Return success response with comprehensive data
        # This includes email data that n8n will use to send notification
        return {
            "status": "success",
            "engagement_id": engagement_id,
            "row_number": workflow_result['row_number'],
            "tracking_sheet_url": workflow_result['tracking_sheet_url'],
            "file_urls": {
                "tracking_sheet": workflow_result['tracking_sheet_url'],
                "pricing_calculator": workflow_result['calculator_url'],
                "rationale": workflow_result['rationale_url']
            },
            "file_info": {
                "file_id": file_id,
                "filename": filename,
                "mime_type": mime_type
            },
            "pricing_data": workflow_result['pricing_data'],
            "email": workflow_result['email'],
            "message": f"File '{filename}' processed successfully. Engagement ID: {engagement_id}. Email notification ready to send."
        }

    except Exception as e:
        logger.error(f"Error processing Google Drive file trigger: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/webhooks/google-drive-file-added/test")
async def test_endpoint():
    """
    Test endpoint to verify the webhook is accessible

    Access this endpoint to confirm:
    - FastAPI server is running
    - Route is registered correctly
    - Endpoint is accessible via ngrok

    Returns:
        Simple status message
    """
    return {
        "status": "online",
        "endpoint": "/webhooks/google-drive-file-added",
        "method": "POST",
        "description": "Google Drive file trigger webhook for n8n",
        "usage": {
            "local": "http://localhost:8000/webhooks/google-drive-file-added",
            "ngrok": "https://YOUR-NGROK-URL/webhooks/google-drive-file-added"
        },
        "expected_payload": {
            "id": "file_id_from_google_drive",
            "name": "filename.txt",
            "mimeType": "text/plain",
            "webViewLink": "https://drive.google.com/file/d/..."
        }
    }
