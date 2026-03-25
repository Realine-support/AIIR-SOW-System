"""
Webhook endpoint for SOW approval
Triggered when user clicks approve/reject button in SOW review email
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from app.workflows import send_sow_and_archive
from app.config import get_config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhooks/approve-sow")
async def approve_sow_webhook(
    engagement_id: str = Query(..., description="Engagement ID"),
    action: str = Query(..., description="Action: approve or reject")
):
    """
    Handle SOW approval webhook

    When user clicks "Approve" in email:
    - Trigger Workflow 3 (Send to Client & Archive)
    - Return success page

    When user clicks "Reject":
    - Mark for manual revision
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
            logger.info(f"SOW approved for engagement {engagement_id}")

            # Trigger Workflow 3
            await send_sow_and_archive(engagement_id, config)

            return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>SOW Approved & Sent</title>
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
    <h1>SOW Approved & Sent!</h1>
    <p><strong>Engagement ID:</strong> {engagement_id}</p>
    <p>The SOW has been sent to the client as a PDF attachment.</p>
    <p>All files have been archived. The engagement is now complete.</p>
    <p style="margin-top: 40px; font-size: 12px; color: #999;">
        You can close this window.
    </p>
</body>
</html>
            """)

        elif action == "reject":
            logger.info(f"SOW rejected for engagement {engagement_id}")

            return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>SOW Rejected</title>
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
    <h1>SOW Rejected</h1>
    <p><strong>Engagement ID:</strong> {engagement_id}</p>
    <p>This SOW has been marked for manual revision. Please edit the SOW document directly and resend when ready.</p>
    <p style="margin-top: 40px; font-size: 12px; color: #999;">
        You can close this window.
    </p>
</body>
</html>
            """)

        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

    except Exception as e:
        logger.error(f"Error in SOW approval webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
