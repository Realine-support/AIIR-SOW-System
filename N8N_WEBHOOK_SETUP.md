# n8n Google Drive Trigger - FastAPI Webhook Setup Guide

This guide explains how to set up the n8n Google Drive trigger with the FastAPI webhook endpoint for event-driven file processing.

## Overview

**Old Approach:** Cron job polls Google Drive every 5 minutes for new files
**New Approach:** n8n triggers immediately when a file is added to Google Drive

### Architecture
```
Google Drive (File Added)
    ↓
n8n Google Drive Trigger (detects file)
    ↓
n8n HTTP Request Node (POST to FastAPI)
    ↓
FastAPI Webhook (/webhooks/google-drive-file-added)
    ↓
Workflow 1: Pricing Simplified
    ↓
Response: {status, engagement_id, file_urls}
```

---

## Part 1: Local Development Setup

### Step 1: Start FastAPI Server Locally

```bash
# Navigate to project directory
cd D:\AIIR\aiir-sow-system

# Activate virtual environment (if not already activated)
venv\Scripts\activate

# Start FastAPI server with auto-reload
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Test the Endpoint

Open a new terminal/command prompt and test the health check:

```bash
# Test general health
curl http://localhost:8000/health

# Test webhook-specific endpoint
curl http://localhost:8000/webhooks/google-drive-file-added/test
```

Expected response:
```json
{
  "status": "online",
  "endpoint": "/webhooks/google-drive-file-added",
  "method": "POST",
  "description": "Google Drive file trigger webhook for n8n"
}
```

---

## Part 2: ngrok Setup (for n8n Integration)

Since n8n needs to send requests to your local FastAPI server, you'll use ngrok to create a public HTTPS URL.

### Step 1: Install ngrok

1. Download from: https://ngrok.com/download
2. Extract to a folder (e.g., `C:\ngrok`)
3. Sign up for a free account at https://dashboard.ngrok.com/signup
4. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
5. Configure authtoken:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### Step 2: Start ngrok Tunnel

In a NEW terminal window (keep FastAPI server running):

```bash
# Navigate to ngrok directory
cd C:\ngrok

# Start tunnel to port 8000
ngrok http 8000
```

You'll see output like:
```
ngrok

Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abcd-1234-5678.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**COPY THE HTTPS URL** (e.g., `https://abcd-1234-5678.ngrok-free.app`)

### Step 3: Test ngrok Tunnel

```bash
# Test the tunnel (replace with your ngrok URL)
curl https://abcd-1234-5678.ngrok-free.app/health
curl https://abcd-1234-5678.ngrok-free.app/webhooks/google-drive-file-added/test
```

---

## Part 3: Configure n8n Workflow

### Step 1: Update HTTP Request Node

In your n8n workflow, configure the HTTP Request node:

**Method:** `POST`

**URL (Local Testing):**
```
http://localhost:8000/webhooks/google-drive-file-added
```

**URL (ngrok):**
```
https://YOUR-NGROK-URL.ngrok-free.app/webhooks/google-drive-file-added
```

**Authentication:** None (as requested)

**Send Body:** `JSON`

**Specify Body:** `Using Fields Below` or `Using Expression`

**Body Content:**
```json
{
  "id": "{{ $json.id }}",
  "name": "{{ $json.name }}",
  "mimeType": "{{ $json.mimeType }}",
  "webViewLink": "{{ $json.webViewLink }}",
  "webContentLink": "{{ $json.webContentLink }}",
  "createdTime": "{{ $json.createdTime }}",
  "modifiedTime": "{{ $json.modifiedTime }}"
}
```

**OR** (simpler - pass entire payload):
```
{{ $json }}
```

**Headers:**
```
Content-Type: application/json
```

### Step 2: Complete n8n Workflow Configuration

Your n8n workflow should look like this:

```
┌─────────────────────────────┐
│  Google Drive Trigger       │
│  - Folder: SOW Templates    │
│  - Event: fileCreated       │
│  - Poll: Every Minute       │
└──────────┬──────────────────┘
           │
           │ Triggers on new file
           │
           ▼
┌─────────────────────────────┐
│  HTTP Request               │
│  - Method: POST             │
│  - URL: ngrok URL           │
│  - Body: {{ $json }}        │
└──────────┬──────────────────┘
           │
           │ Receives response
           │
           ▼
    Response shows:
    - status: "success"
    - engagement_id: "ENG-..."
    - file_urls:
        - sow_template
        - pricing_calculator
```

### Step 3: Test the Integration

1. **Activate the n8n workflow**
2. **Add a test file to the Google Drive folder**
   - Folder: "SOW Templates" (ID: `1z_5jdY2Mvv0cZ6Am8W4__RKuSMsIFSqu`)
   - File type: `.txt` (transcript) or `.docx`
3. **Watch n8n execution**
   - n8n should detect the file within 1 minute
   - HTTP Request node should POST to FastAPI
   - Response should show success
4. **Check FastAPI logs**
   - You should see log entries for file processing
5. **Verify in Google Sheets**
   - Check Tracker sheet for new engagement
   - Check Calculator sheet for pricing details

---

## Part 4: Expected Response Format

When n8n sends a POST request, FastAPI will respond with:

### Success Response (200 OK)
```json
{
  "status": "success",
  "engagement_id": "ENG-20260319-ABC123",
  "file_urls": {
    "sow_template": "https://docs.google.com/document/d/...",
    "pricing_calculator": "https://docs.google.com/spreadsheets/d/..."
  },
  "file_info": {
    "file_id": "1a2b3c4d5e6f",
    "filename": "transcript.txt",
    "mime_type": "text/plain"
  },
  "message": "File 'transcript.txt' processed successfully. Engagement ID: ENG-20260319-ABC123",
  "tracker_sheet_url": "https://docs.google.com/spreadsheets/d/..."
}
```

### Error Response (400/500)
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Part 5: Monitoring and Debugging

### View FastAPI Logs

In the terminal running FastAPI, you'll see:
```
INFO:     127.0.0.1:52000 - "POST /webhooks/google-drive-file-added HTTP/1.1" 200 OK
INFO:     Received Google Drive file trigger: {...}
INFO:     Processing file: transcript.txt (ID: 1a2b3c4d5e6f, MIME: text/plain)
INFO:     Successfully processed file transcript.txt → Engagement: ENG-20260319-ABC123
```

### View ngrok Logs

ngrok provides a web interface at: `http://127.0.0.1:4040`

This shows:
- All HTTP requests going through the tunnel
- Request/response bodies
- Timing information
- Errors

### Debug Checklist

If the webhook isn't working:

1. **Check FastAPI is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check ngrok tunnel is active:**
   ```bash
   curl https://YOUR-NGROK-URL.ngrok-free.app/health
   ```

3. **Check n8n workflow is activated:**
   - Green "Active" badge should be visible

4. **Check Google Drive folder ID is correct:**
   - Verify `1z_5jdY2Mvv0cZ6Am8W4__RKuSMsIFSqu` is the right folder

5. **Check n8n execution logs:**
   - Click on workflow executions
   - View each node's output
   - Check for error messages

6. **Test with manual execution:**
   - In n8n, click "Execute Workflow"
   - This tests the workflow without waiting for new files

---

## Part 6: Production Deployment (Optional)

For production use (instead of ngrok):

### Option 1: Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project directory
cd D:\AIIR\aiir-sow-system
vercel

# Get production URL
# Update n8n HTTP Request node with Vercel URL
```

### Option 2: Deploy to Railway/Render

Both platforms support FastAPI apps:
- Railway: https://railway.app
- Render: https://render.com

### Option 3: Cloud VM (AWS/GCP/Azure)

Deploy FastAPI on a cloud VM with:
- Public IP address
- SSL certificate (Let's Encrypt)
- Reverse proxy (nginx)

---

## Part 7: Testing Without n8n

You can test the webhook directly using curl:

```bash
# Test POST request with sample data
curl -X POST http://localhost:8000/webhooks/google-drive-file-added \
  -H "Content-Type: application/json" \
  -d '{
    "id": "1a2b3c4d5e6f7g8h9i0j",
    "name": "test_transcript.txt",
    "mimeType": "text/plain",
    "webViewLink": "https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view"
  }'
```

**Note:** This requires a valid file ID in Google Drive.

---

## Part 8: Security Notes

**Current Setup:** No authentication (as requested)

**For Production, Consider Adding:**

1. **API Key Authentication:**
   ```python
   from fastapi import Header, HTTPException

   async def verify_api_key(x_api_key: str = Header(...)):
       if x_api_key != "your-secret-key":
           raise HTTPException(status_code=401)
   ```

2. **IP Whitelisting:**
   - Only allow requests from n8n server IP

3. **HMAC Signature Verification:**
   - n8n can sign requests with a secret
   - FastAPI verifies signature before processing

4. **Rate Limiting:**
   ```bash
   pip install slowapi
   ```

---

## Part 9: Troubleshooting Common Issues

### Issue 1: "Connection Refused" from n8n

**Cause:** FastAPI server is not running
**Solution:** Start FastAPI with `uvicorn api.index:app --reload --host 0.0.0.0 --port 8000`

### Issue 2: "404 Not Found"

**Cause:** Wrong URL in n8n
**Solution:** Use `/webhooks/google-drive-file-added` (not `/api/webhooks/...`)

### Issue 3: "400 Bad Request - Missing required fields"

**Cause:** n8n is not sending file metadata correctly
**Solution:** In n8n HTTP Request, use `{{ $json }}` as body

### Issue 4: ngrok tunnel "Not Found"

**Cause:** ngrok tunnel expired (free tier resets URLs)
**Solution:** Restart ngrok, copy new URL to n8n

### Issue 5: "500 Internal Server Error"

**Cause:** Error in workflow processing
**Solution:** Check FastAPI logs for stack trace

---

## Quick Reference

### URLs

| Environment | URL |
|-------------|-----|
| Local API | http://localhost:8000 |
| Local Webhook | http://localhost:8000/webhooks/google-drive-file-added |
| Local Test | http://localhost:8000/webhooks/google-drive-file-added/test |
| Local Health | http://localhost:8000/health |
| ngrok Tunnel | https://YOUR-NGROK-URL.ngrok-free.app |
| ngrok Inspector | http://127.0.0.1:4040 |

### Commands

```bash
# Start FastAPI
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000

# Start ngrok
ngrok http 8000

# Test health
curl http://localhost:8000/health

# Test webhook
curl http://localhost:8000/webhooks/google-drive-file-added/test
```

### n8n HTTP Request Configuration

```
Method: POST
URL: https://YOUR-NGROK-URL.ngrok-free.app/webhooks/google-drive-file-added
Body: {{ $json }}
Headers: Content-Type: application/json
```

---

## Next Steps

1. ✅ Start FastAPI server locally
2. ✅ Test health endpoint
3. ✅ Start ngrok tunnel
4. ✅ Update n8n HTTP Request node with ngrok URL
5. ✅ Activate n8n workflow
6. ✅ Add test file to Google Drive
7. ✅ Verify response in n8n
8. ✅ Check Tracker and Calculator sheets
9. ✅ Monitor logs for any issues

---

## Support

If you encounter issues:
1. Check FastAPI logs
2. Check ngrok web interface (http://127.0.0.1:4040)
3. Check n8n execution logs
4. Verify .env file has all required variables
5. Ensure Google credentials are valid

Happy automating!
