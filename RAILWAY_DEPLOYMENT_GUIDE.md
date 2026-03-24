# Railway Production Deployment Guide

## 🚀 Complete Step-by-Step Production Deployment

This guide will help you deploy the AIIR SOW System to Railway and configure n8n for production use.

---

## STEP 1: Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `Realine-support/AIIR-SOW-System`
5. Railway will auto-detect it's a Python application
6. Wait for initial deployment to complete
7. **Copy your deployment URL** (e.g., `https://aiir-sow-system.up.railway.app`)

---

## STEP 2: Configure Environment Variables in Railway

### How to Add Variables:
1. Go to your Railway project
2. Click on your service
3. Go to **"Variables"** tab
4. Click **"New Variable"** or **"Add Variables"**
5. Paste all variables below

### Required Environment Variables:

```env
# Copy these from your local .env file - DO NOT commit actual values to GitHub
# These are stored securely in Railway's environment variables

OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
TRACKER_SHEET_ID=your-tracker-sheet-id
TRACKER_TAB_NAME=Tracker
CALCULATOR_SHEET_ID=your-calculator-sheet-id
CALCULATOR_TAB_NAME=Calculator
SHARED_DRIVE_ID=your-shared-drive-id
CALCULATOR_TEMPLATE_ID=your-calculator-template-id
SOW_TEMPLATE_DOC_ID=your-sow-template-doc-id
TRANSCRIPTS_FOLDER_ID=your-transcripts-folder-id
SOW_TEMPLATES_FOLDER_ID=your-sow-templates-folder-id
CLIENT_DOCUMENTS_FOLDER_ID=your-client-documents-folder-id
RATIONALES_FOLDER_ID=your-rationales-folder-id
CLIENT_MASTER_FOLDER_ID=your-client-master-folder-id
ARCHIVE_FOLDER_ID=your-archive-folder-id
GMAIL_SEND_AS=your-email@gmail.com
REVIEW_EMAIL_TO=your-email@gmail.com
CLIENT_EMAIL_FROM=your-email@gmail.com
UPSTASH_REDIS_REST_URL=your-upstash-redis-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-token
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
```

**⚠️ IMPORTANT:** Use the actual values from your local `D:\AIIR\aiir-sow-system\.env` file when adding these to Railway. The placeholders above are just examples.

### 🔴 IMPORTANT: Update These After Deployment

Once you have your Railway URL, add these variables with YOUR actual Railway URL:

```env
BASE_URL=https://YOUR-ACTUAL-RAILWAY-URL.up.railway.app
APPROVE_PRICING_WEBHOOK_URL=https://YOUR-ACTUAL-RAILWAY-URL.up.railway.app/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=https://YOUR-ACTUAL-RAILWAY-URL.up.railway.app/webhooks/approve-sow
```

**Example (if your Railway URL is `https://aiir-sow-system.up.railway.app`):**
```env
BASE_URL=https://aiir-sow-system.up.railway.app
APPROVE_PRICING_WEBHOOK_URL=https://aiir-sow-system.up.railway.app/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=https://aiir-sow-system.up.railway.app/webhooks/approve-sow
```

---

## STEP 3: Add Google Service Account Credentials

Railway cannot access local files, so you need to provide Google credentials as an environment variable.

### Option A: Upload JSON Content Directly (Recommended)

1. **Open the file:** `D:\AIIR\sales-ai-agent-484003-fcd77f3c1a42.json`
2. **Copy the ENTIRE contents** (it should be a single line of JSON)
3. **Add to Railway as a new variable:**
   ```
   Variable Name: GOOGLE_CREDENTIALS_JSON
   Value: (paste the entire JSON content)
   ```

### Option B: Convert to Base64

Run this PowerShell command:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("D:\AIIR\sales-ai-agent-484003-fcd77f3c1a42.json"))
```

Then add to Railway:
```
Variable Name: GOOGLE_CREDENTIALS_BASE64
Value: (paste the base64 string)
```

**Note:** If using Option A or B, you'll need code changes to read from environment variables instead of file paths.

### Option C: Use Railway's File Upload (Easiest - No Code Changes)

1. In Railway, go to your service
2. Click "Settings" tab
3. Look for "Volumes" or "Persistent Storage"
4. Upload `sales-ai-agent-484003-fcd77f3c1a42.json`
5. Update the environment variable:
   ```
   GOOGLE_CREDENTIALS_PATH=/app/sales-ai-agent-484003-fcd77f3c1a42.json
   ```

**For now, let's use the simplest approach - I'll update the code to support environment variable credentials.**

---

## STEP 4: Update n8n Workflow Configuration

### What You Need to Change:

In your n8n workflow, update the **"POST to FastAPI Webhook"** HTTP Request node:

**Current Configuration (Development):**
```
Method: POST
URL: REPLACE_WITH_YOUR_NGROK_URL/webhooks/google-drive-file-added
```

**New Configuration (Production):**
```
Method: POST
URL: https://YOUR-RAILWAY-URL.up.railway.app/webhooks/google-drive-file-added
Body: {{ $json }}
Headers: Content-Type: application/json
Timeout: 60000
```

### Step-by-Step in n8n:

1. Open your n8n workflow: "Google Drive → FastAPI Webhook"
2. Click on the **"POST to FastAPI Webhook"** node
3. Update the **URL** field with your Railway URL
4. **Save** the workflow
5. **Activate** the workflow (toggle switch to ON)

---

## STEP 5: Test Your Production Deployment

### Test 1: Health Check

Open your browser or use curl:

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "endpoints": {
    "approve_pricing": "/webhooks/approve-pricing",
    "approve_sow": "/webhooks/approve-sow",
    "google_drive_trigger": "/webhooks/google-drive-file-added",
    "google_drive_trigger_test": "/webhooks/google-drive-file-added/test",
    "watch_transcripts": "/cron/watch-transcripts"
  }
}
```

### Test 2: Webhook Test Endpoint

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/webhooks/google-drive-file-added/test
```

**Expected Response:**
```json
{
  "status": "online",
  "endpoint": "/webhooks/google-drive-file-added",
  "method": "POST",
  "description": "Google Drive file trigger webhook for n8n"
}
```

### Test 3: End-to-End Integration Test

1. **Ensure n8n workflow is ACTIVE**
2. **Upload a test transcript file** to Google Drive folder:
   - Folder ID: `1z_5jdY2Mvv0cZ6Am8W4__RKuSMsIFSqu`
   - File type: `.txt` or `.docx`
3. **Wait 1 minute** for n8n to detect the file
4. **Check n8n execution logs** (should show success)
5. **Verify in Google Sheets:**
   - Check Tracker sheet for new engagement row
   - Check Calculator sheet for pricing details
6. **Check Railway logs** for processing activity

---

## STEP 6: Monitor Your Production System

### Railway Logs

1. Go to Railway → Your Project → Service
2. Click **"Logs"** tab
3. Watch for:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete.
   INFO:     POST /webhooks/google-drive-file-added HTTP/1.1 200 OK
   ```

### n8n Execution Monitoring

1. Go to n8n → **Executions** tab
2. View each execution
3. Check node outputs for errors
4. Verify webhook response shows success

### Google Sheets Verification

- **Tracker Sheet:** https://docs.google.com/spreadsheets/d/1_9faJK4jCs-jhbKyI1HuF01CCzY6H3DlzUQKuhSUYtU
- **Calculator Sheet:** https://docs.google.com/spreadsheets/d/1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM

---

## 📍 All Production Endpoints Reference

| Endpoint | Full URL | Purpose | Update in n8n? |
|----------|----------|---------|----------------|
| **Main Webhook** | `https://YOUR-RAILWAY-URL/webhooks/google-drive-file-added` | Triggered by n8n when file added to Drive | **YES ✅** |
| Health Check | `https://YOUR-RAILWAY-URL/health` | API health status | No |
| Root | `https://YOUR-RAILWAY-URL/` | Service info | No |
| Test Endpoint | `https://YOUR-RAILWAY-URL/webhooks/google-drive-file-added/test` | Test webhook availability | No |
| Approve Pricing | `https://YOUR-RAILWAY-URL/webhooks/approve-pricing` | Email approval links | No (auto-used) |
| Approve SOW | `https://YOUR-RAILWAY-URL/webhooks/approve-sow` | Email approval links | No (auto-used) |
| Cron Job | `https://YOUR-RAILWAY-URL/cron/watch-transcripts` | Backup polling (optional) | No |

---

## 🚨 Pre-Production Go-Live Checklist

Before going live, verify all of these:

### Railway Configuration
- [ ] Repository deployed successfully on Railway
- [ ] All environment variables added (see STEP 2)
- [ ] `BASE_URL` updated with actual Railway URL
- [ ] `APPROVE_PRICING_WEBHOOK_URL` updated with Railway URL
- [ ] `APPROVE_SOW_WEBHOOK_URL` updated with Railway URL
- [ ] Google service account credentials configured
- [ ] Deployment shows "Active" status
- [ ] No build errors in Railway logs

### Testing
- [ ] Health check endpoint returns 200 OK
- [ ] Test endpoint returns correct response
- [ ] Railway logs show "Application startup complete"

### n8n Configuration
- [ ] HTTP Request node URL updated with Railway URL
- [ ] Workflow saved
- [ ] Workflow activated (green toggle)
- [ ] Google Drive trigger configured for correct folder

### End-to-End Verification
- [ ] Test file uploaded to Google Drive
- [ ] n8n workflow triggered successfully
- [ ] n8n HTTP Request returns 200 OK
- [ ] Tracker sheet updated with new engagement
- [ ] Calculator sheet updated with pricing data
- [ ] Railway logs show successful processing
- [ ] No errors in Railway or n8n logs

### Email Notifications (Optional)
- [ ] Test email approval link for pricing
- [ ] Test email approval link for SOW
- [ ] Verify email delivery

---

## 🔧 Troubleshooting Common Issues

### Issue 1: Railway Build Fails

**Error:** "ModuleNotFoundError" or dependency issues

**Solution:**
- Check `requirements.txt` is in the repository
- Verify all dependencies are listed
- Check Railway build logs for specific errors

### Issue 2: "503 Service Unavailable"

**Error:** Railway URL returns 503

**Solution:**
- Check Railway logs for startup errors
- Verify all environment variables are set
- Ensure Google credentials are configured correctly
- Check for missing dependencies

### Issue 3: n8n Shows "Connection Refused"

**Error:** n8n cannot reach Railway endpoint

**Solution:**
- Verify Railway URL is correct (no typos)
- Ensure Railway deployment is active
- Test health endpoint manually in browser
- Check Railway firewall/network settings

### Issue 4: "400 Bad Request - Missing required fields"

**Error:** FastAPI rejects n8n payload

**Solution:**
- Ensure n8n sends `{{ $json }}` as body
- Verify Content-Type header is `application/json`
- Check n8n execution logs for actual payload sent

### Issue 5: Google API Authentication Errors

**Error:** "Could not load credentials" or "Invalid grant"

**Solution:**
- Verify `GOOGLE_CREDENTIALS_JSON` or `GOOGLE_CREDENTIALS_PATH` is correct
- Ensure service account has access to Google Drive/Sheets
- Check service account email matches configuration
- Verify shared drive permissions

### Issue 6: Redis Connection Errors

**Error:** Cannot connect to Upstash Redis

**Solution:**
- Verify `UPSTASH_REDIS_REST_URL` is correct
- Verify `UPSTASH_REDIS_REST_TOKEN` is correct
- Check Upstash dashboard for service status
- Ensure Upstash allows connections from Railway IPs

---

## 🎯 Quick Reference: What Changed from Development to Production

| Component | Development | Production |
|-----------|-------------|------------|
| **API URL** | `http://localhost:8000` | `https://YOUR-RAILWAY-URL.up.railway.app` |
| **n8n Webhook URL** | ngrok tunnel | Railway URL |
| **Environment** | `development` | `production` |
| **Debug Mode** | `true` | `false` |
| **Credentials** | Local file path | Environment variable |
| **Base URL** | `http://localhost:8000` | Railway URL |

---

## 📞 Next Steps After Deployment

1. **Monitor for 24 hours:**
   - Check Railway logs daily
   - Monitor n8n executions
   - Verify Google Sheets updates

2. **Set up alerts (optional):**
   - Railway can send deployment notifications
   - n8n can send error notifications
   - Set up Uptime monitoring (e.g., UptimeRobot)

3. **Backup strategy:**
   - Regularly export Google Sheets
   - Monitor Upstash Redis usage
   - Keep track of processed engagements

4. **Performance optimization:**
   - Monitor Railway resource usage
   - Optimize if response times are slow
   - Consider upgrading Railway plan if needed

---

## 🎉 You're Ready for Production!

Once you complete all steps above, your AIIR SOW System will be fully operational in production. The system will automatically:

1. ✅ Detect new transcripts in Google Drive
2. ✅ Extract client information using AI
3. ✅ Calculate pricing based on business rules
4. ✅ Update Tracker and Calculator sheets
5. ✅ Generate SOW documents
6. ✅ Send approval emails
7. ✅ Archive completed engagements

**Happy automating! 🚀**
