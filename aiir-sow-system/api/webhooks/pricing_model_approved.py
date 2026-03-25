"""
Webhook endpoint for n8n Google Sheets trigger
Triggered when Pricing Model Status is changed to "Approved" in tracking sheet
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.workflows.workflow_2_sow_generation import generate_sow_from_approval
from app.config import get_config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PricingModelApprovalPayload(BaseModel):
    """
    Expected payload from n8n Google Sheets Trigger

    The Google Sheets Trigger node sends row data when a cell is updated
    """
    engagement_id: str


@router.post("/webhooks/pricing-model-approved")
async def pricing_model_approved(
    engagement_id: str = Query(..., description="Engagement ID from tracking sheet")
):
    """
    Handle pricing model approval from n8n Google Sheets Trigger

    Workflow:
    1. Receive engagement_id from n8n (when Column U changes to "Approved")
    2. Trigger Workflow 2 (SOW Generation)
    3. Return success with SOW URL and email data

    n8n Configuration:
    - Trigger: Google Sheets Trigger (watches Column U in Tracker sheet)
    - Filter: Only trigger when Column U = "Approved"
    - HTTP Request Node: POST to this endpoint
    - Method: POST
    - URL: https://YOUR-API-URL/webhooks/pricing-model-approved?engagement_id={{engagement_id}}
    - OR send in body: { "engagement_id": "{{ $json['Engagement ID'] }}" }

    Returns:
        JSON response with:
            - status: "success"
            - engagement_id: str
            - sow_url: str
            - email: dict (for n8n to send notification)
    """
    try:
        config = get_config()

        logger.info(f"Received pricing model approval for engagement: {engagement_id}")

        if not engagement_id:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: 'engagement_id' is required"
            )

        # Trigger Workflow 2 (SOW Generation)
        # This will:
        # 1. Read engagement data from Tracker
        # 2. Create SOW from template
        # 3. Replace placeholders
        # 4. Update Tracker with SOW URL
        # 5. Generate email HTML
        # 6. Return comprehensive data including email
        workflow_result = await generate_sow_from_approval(
            engagement_id=engagement_id,
            config=config
        )

        logger.info(f"Successfully generated SOW for engagement: {engagement_id}")

        # Return success response with comprehensive data
        # This includes email data that n8n will use to send notification
        return {
            "status": "success",
            "engagement_id": engagement_id,
            "sow_document_id": workflow_result['sow_document_id'],
            "sow_url": workflow_result['sow_url'],
            "row_number": workflow_result['row_number'],
            "tracking_sheet_url": workflow_result['tracking_sheet_url'],
            "file_urls": {
                "sow": workflow_result['sow_url'],
                "tracking_sheet": workflow_result['tracking_sheet_url'],
                "calculator": workflow_result['calculator_url'],
                "rationale": workflow_result['rationale_url']
            },
            "engagement_data": workflow_result['engagement_data'],
            "email": workflow_result['email'],
            "message": f"SOW generated successfully for {workflow_result['engagement_data']['client_company']}. Email notification ready to send."
        }

    except Exception as e:
        logger.error(f"Error processing pricing model approval: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SOW: {str(e)}"
        )


@router.get("/webhooks/pricing-model-approved/test")
async def test_endpoint():
    """
    Test endpoint to verify the webhook is accessible

    Access this endpoint to confirm:
    - FastAPI server is running
    - Route is registered correctly
    - Endpoint is accessible

    Returns:
        Simple status message
    """
    return {
        "status": "online",
        "endpoint": "/webhooks/pricing-model-approved",
        "method": "POST",
        "description": "Pricing model approval webhook for n8n",
        "usage": {
            "query_param": "POST /webhooks/pricing-model-approved?engagement_id=ENG-123",
            "json_body": "POST /webhooks/pricing-model-approved with body: { \"engagement_id\": \"ENG-123\" }"
        },
        "expected_payload": {
            "engagement_id": "CLIENTNAME-20260324-1234"
        },
        "trigger": "n8n Google Sheets Trigger watches Column U (Pricing Model Status)",
        "filter": "Only triggers when Column U changes to 'Approved'"
    }
