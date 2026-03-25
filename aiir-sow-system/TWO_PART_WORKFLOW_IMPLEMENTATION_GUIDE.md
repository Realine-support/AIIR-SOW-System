# Two-Part Workflow Implementation Guide

## Overview

This guide explains the new two-part workflow system with automatic email notifications:

**Part 1:** Transcript Upload → Pricing Model Generation → Email Notification
**Part 2:** Pricing Model Approval → SOW Generation → Email Notification

---

## System Architecture

```
PART 1: Pricing Model Generation
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Transcript     n8n         HTTP API      Pricing Model   Email    │
│  Uploaded   →  Trigger  →   Call     →    Generated   →  Sent      │
│                                                                     │
│  Google        Detects      POST to       - Calculator             │
│  Drive         new file     /webhooks/    - Rationale              │
│                             google-        - Tracker Row            │
│                             drive-file-    - Email HTML             │
│                             added                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

PART 2: SOW Generation on Approval
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Column U      n8n          HTTP API      SOW            Email     │
│  Changed to → Trigger  →    Call     →    Generated  →  Sent       │
│  "Approved"                                                         │
│                                                                     │
│  Tracking      Watches      POST to       - SOW Doc                │
│  Sheet         Column U     /webhooks/    - Email HTML             │
│                             pricing-                                │
│                             model-                                  │
│                             approved                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Changes Made

### 1. Tracking Sheet Structure
**NEW COLUMN ADDED:**
- **Column U: "Pricing Model Status"**
  - Options: "Pending Review", "Approved", "Disapproved"
  - This column triggers Part 2 when set to "Approved"

### 2. New Email Templates

#### `templates/pricing_model_ready_email.html`
- Sent after pricing model is created
- Includes links to: Tracking Sheet, Calculator, Rationale
- Instructions to update Column U

#### `templates/sow_generated_email.html`
- Sent after SOW is generated
- Includes links to: SOW Document, Tracking Sheet, Calculator, Rationale
- Next steps for review and client delivery

### 3. Modified Workflows

#### `app/workflows/workflow_1_pricing_simplified.py`
**Changes:**
- Now returns dict instead of string
- Adds Column U = "Pending Review" to tracker row
- Generates email HTML using Jinja2 template
- Returns comprehensive data including email

**Return structure:**
```python
{
    'engagement_id': str,
    'row_number': int,
    'tracking_sheet_url': str,
    'calculator_url': str,
    'rationale_url': str,
    'email': {
        'subject': str,
        'html_body': str,
        'to': str,
        'client_name': str
    },
    'pricing_data': {...}
}
```

#### `app/workflows/workflow_2_sow_generation.py`
**Changes:**
- Removed Gmail and Redis dependencies
- Now returns dict instead of string
- Generates email HTML using Jinja2 template
- Returns comprehensive data including email

**Return structure:**
```python
{
    'sow_document_id': str,
    'sow_url': str,
    'engagement_id': str,
    'row_number': int,
    'tracking_sheet_url': str,
    'calculator_url': str,
    'rationale_url': str,
    'email': {
        'subject': str,
        'html_body': str,
        'to': str,
        'client_name': str,
        'decision_maker_email': str
    },
    'engagement_data': {...}
}
```

### 4. Updated API Endpoints

#### `api/webhooks/google_drive_trigger.py`
**Changes:**
- Updated to handle dict return from workflow
- Returns email data in response for n8n to use

**Response structure:**
```json
{
    "status": "success",
    "engagement_id": "...",
    "row_number": 5,
    "tracking_sheet_url": "...",
    "file_urls": {
        "tracking_sheet": "...",
        "pricing_calculator": "...",
        "rationale": "..."
    },
    "pricing_data": {...},
    "email": {
        "subject": "...",
        "html_body": "<html>...</html>",
        "to": "reviewer@example.com",
        "client_name": "..."
    },
    "message": "..."
}
```

### 5. New Webhook Endpoint

#### `api/webhooks/pricing_model_approved.py`
**NEW FILE**

**Purpose:** Handle pricing model approval from n8n Google Sheets trigger

**Endpoint:** `POST /webhooks/pricing-model-approved?engagement_id=...`

**Response structure:**
```json
{
    "status": "success",
    "engagement_id": "...",
    "sow_document_id": "...",
    "sow_url": "...",
    "row_number": 5,
    "tracking_sheet_url": "...",
    "file_urls": {
        "sow": "...",
        "tracking_sheet": "...",
        "calculator": "...",
        "rationale": "..."
    },
    "engagement_data": {...},
    "email": {
        "subject": "...",
        "html_body": "<html>...</html>",
        "to": "...",
        "client_name": "...",
        "decision_maker_email": "..."
    },
    "message": "..."
}
```

### 6. Updated API Router

#### `api/index.py`
- Added import for `pricing_model_approved`
- Registered new router
- Added endpoints to health check

---

## Setup Instructions

### Step 1: Update Tracking Sheet

1. Open your Tracking Sheet in Google Sheets
2. Add a new column after Column T (Updated At):
   - **Column U: "Pricing Model Status"**
3. Set up data validation for Column U:
   - Select column U
   - Data → Data validation
   - Criteria: List from a range or List of items
   - Values: `Pending Review, Approved, Disapproved`
   - Show dropdown in cell: YES
4. Format the column with conditional formatting (optional):
   - Pending Review: Yellow
   - Approved: Green
   - Disapproved: Red

### Step 2: Configure n8n Workflow 1 (Pricing Model Generation)

**Workflow Structure:**
```
[1] Google Drive Trigger
  ↓
[2] HTTP Request (to FastAPI)
  ↓
[3] Send Email
```

**Node 1: Google Drive Trigger**
- Trigger: Google Drive Trigger
- Folder ID: Your transcripts folder ID
- Event: file.created
- Poll interval: Every 1 minute (or as needed)

**Node 2: HTTP Request**
- Method: POST
- URL: `{{your-api-url}}/webhooks/google-drive-file-added`
- Authentication: None
- Send Body: JSON
- Body: `{{ $json }}`

**Node 3: Send Email**
- Email Provider: Gmail/SendGrid/SMTP (your choice)
- To: `{{ $json.email.to }}`
- Subject: `{{ $json.email.subject }}`
- HTML Body: `{{ $json.email.html_body }}`

**Testing:**
- Upload a test transcript to Google Drive
- Check n8n execution logs
- Verify email received
- Check Tracking Sheet for new row with Column U = "Pending Review"

### Step 3: Configure n8n Workflow 2 (SOW Generation on Approval)

**Workflow Structure:**
```
[1] Google Sheets Trigger
  ↓
[2] Filter (Only "Approved")
  ↓
[3] HTTP Request (to FastAPI)
  ↓
[4] Send Email
```

**Node 1: Google Sheets Trigger**
- Trigger: Google Sheets
- Spreadsheet: Your Tracking Sheet
- Sheet: Tracker
- Trigger On: Row Updated
- Watch specific column: Column U (Pricing Model Status)
- Poll interval: Every 1 minute

**Node 2: Filter (IF Node)**
- Condition: `{{ $json["Pricing Model Status"] }} equals "Approved"`
- If false: Stop workflow

**Node 3: HTTP Request**
- Method: POST
- URL: `{{your-api-url}}/webhooks/pricing-model-approved?engagement_id={{ $json["Engagement ID"] }}`
- Authentication: None

**Node 4: Send Email**
- Email Provider: Gmail/SendGrid/SMTP (your choice)
- To: `{{ $json.email.to }}`
- Subject: `{{ $json.email.subject }}`
- HTML Body: `{{ $json.email.html_body }}`

**Testing:**
- In Tracking Sheet, change Column U to "Approved" for a test row
- Check n8n execution logs
- Verify SOW document created
- Verify email received
- Check Tracking Sheet for SOW URL in Column Q

---

## Testing Checklist

### Part 1: Pricing Model Generation
- [ ] Upload transcript to Google Drive
- [ ] n8n Workflow 1 triggers
- [ ] API processes transcript successfully
- [ ] Tracker sheet updated with new row
- [ ] Column U set to "Pending Review"
- [ ] Calculator sheet updated
- [ ] Rationale document created
- [ ] Email sent to reviewer
- [ ] Email contains correct links

### Part 2: SOW Generation
- [ ] Change Column U to "Approved" in Tracker
- [ ] n8n Workflow 2 triggers
- [ ] API generates SOW successfully
- [ ] SOW document created from template
- [ ] Tracker sheet updated with SOW URL (Column Q)
- [ ] Email sent to reviewer
- [ ] Email contains correct SOW link

---

## Troubleshooting

### Issue: Email not sent in Part 1
**Check:**
1. n8n Node 3 configuration
2. API response contains `email` object
3. Email provider credentials in n8n

**Solution:**
- Check n8n execution logs for Node 3
- Verify API response structure
- Test email node separately

### Issue: n8n Workflow 2 not triggering
**Check:**
1. Google Sheets Trigger configured correctly
2. Column U has correct name
3. Filter node condition correct

**Solution:**
- Manually execute Workflow 2 to test
- Check n8n trigger settings
- Verify sheet column name matches exactly

### Issue: SOW not generated
**Check:**
1. Engagement ID passed correctly
2. Row exists in Tracker sheet
3. SOW template ID configured

**Solution:**
- Check API logs for errors
- Verify engagement ID in request
- Test endpoint: `/webhooks/pricing-model-approved/test`

---

## API Endpoints Reference

### Health Check
```bash
GET /health
```

### Test Endpoints
```bash
GET /webhooks/google-drive-file-added/test
GET /webhooks/pricing-model-approved/test
```

### Production Endpoints
```bash
POST /webhooks/google-drive-file-added
POST /webhooks/pricing-model-approved?engagement_id=XXX
```

---

## Environment Variables

No new environment variables required. The system uses existing configuration from `.env`:

- `TRACKER_SHEET_ID` - Tracking sheet ID
- `REVIEW_EMAIL_TO` - Email address for notifications
- Other existing variables

---

## Column Mapping Reference

| Column | Field | Value After Part 1 | Value After Part 2 |
|--------|-------|-------------------|-------------------|
| A | Engagement ID | Generated ID | (unchanged) |
| B | Client Company | Extracted | (unchanged) |
| ... | ... | ... | ... |
| Q | SOW URL | (empty) | SOW document link |
| R | Status | "Pending Review" | "SOW Generated" |
| U | **Pricing Model Status** | **"Pending Review"** | **"Approved"** |

---

## Next Steps After Implementation

1. **Test thoroughly** with sample transcripts
2. **Train users** on the new Column U workflow
3. **Monitor emails** for delivery issues
4. **Document** any custom modifications
5. **Set up alerts** for failed workflows in n8n

---

## Support

For issues or questions:
1. Check FastAPI logs: `tail -f logs/app.log`
2. Check n8n execution logs
3. Test endpoints using `/test` routes
4. Review this documentation

---

## Summary

The new two-part workflow:
1. **Automatically notifies** reviewers when pricing models are ready
2. **Triggers SOW generation** automatically when approved
3. **Sends confirmation emails** at each step
4. **Maintains tracking** in the Google Sheet
5. **Reduces manual steps** and speeds up the process

All email content is generated by the Python backend, ensuring consistency and easy customization.
