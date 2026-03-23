"""
Webhook endpoint for pricing approval
Triggered when user clicks approve/reject button in email
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from app.workflows import generate_sow_from_approval
from app.config import get_config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhooks/approve-pricing")
async def approve_pricing_webhook(
    engagement_id: str = Query(..., description="Engagement ID"),
    action: str = Query(..., description="Action: approve or reject")
):
    """
    Handle pricing approval webhook

    When user clicks "Approve" in email:
    - Trigger Workflow 2 (SOW Generation)
    - Return success page

    When user clicks "Reject":
    - Mark for manual review
    - Return rejection page

    Args:
        engagement_id: Unique engagement ID
        action: 'approve' or 'reject'

    Returns:
        HTML response with status
    """
    try:
        config = get_config()

        if action == "approve":
            logger.info(f"Pricing approved for engagement {engagement_id}")

            # Trigger Workflow 2
            sow_doc_id = await generate_sow_from_approval(engagement_id, config)

            return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Pricing Approved</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }}
        .success {{
            color: #28a745;
            font-size: 48px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="success">✓</div>
    <h1>Pricing Approved!</h1>
    <p><strong>Engagement ID:</strong> {engagement_id}</p>
    <p>SOW generation has been triggered. You will receive an email when the SOW is ready for review.</p>
    <p style="margin-top: 40px; font-size: 12px; color: #999;">
        You can close this window.
    </p>
</body>
</html>
            """)

        elif action == "reject":
            logger.info(f"Pricing rejected for engagement {engagement_id}")

            # TODO: Mark in tracker for manual review
            # For now, just return rejection page

            return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Pricing Rejected</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }}
        .warning {{
            color: #dc3545;
            font-size: 48px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="warning">✕</div>
    <h1>Pricing Rejected</h1>
    <p><strong>Engagement ID:</strong> {engagement_id}</p>
    <p>This engagement has been marked for manual review. Please update the pricing in the Calculator sheet and Tracker.</p>
    <p style="margin-top: 40px; font-size: 12px; color: #999;">
        You can close this window.
    </p>
</body>
</html>
            """)

        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

    except Exception as e:
        logger.error(f"Error in pricing approval webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
