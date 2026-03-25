# n8n Google Drive Webhook - Quick Start Guide

## Overview

This system uses **event-driven triggers** instead of polling. When a file is added to Google Drive, n8n immediately sends it to FastAPI for processing.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Start FastAPI Server

```bash
cd D:\AIIR\aiir-sow-system
venv\Scripts\activate
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Test the Endpoint

```bash
# In a new terminal
cd D:\AIIR\aiir-sow-system
venv\Scripts\activate
python test_webhook.py
```

You should see:
```
✅ Health Check PASSED
✅ Webhook Test Endpoint PASSED
✅ Webhook POST PASSED
🎉 All tests passed!
```

### Step 3: Start ngrok Tunnel

```bash
# In a new terminal
ngrok http 8000
```

**Copy the HTTPS URL** (e.g., `https://abcd-1234.ngrok-free.app`)

### Step 4: Configure n8n

1. Open your n8n workflow
2. Edit the **HTTP Request** node
3. Set URL to: `https://YOUR-NGROK-URL.ngrok-free.app/webhooks/google-drive-file-added`
4. Set Method: `POST`
5. Set Body: `{{ $json }}`
6. **Activate the workflow**

### Step 5: Test End-to-End

1. Add a `.txt` file to your Google Drive folder
2. Watch n8n detect it (within 1 minute)
3. Check the HTTP Request node output - should show:
   ```json
   {
     "status": "success",
     "engagement_id": "ENG-20260319-...",
     "file_urls": {
       "sow_template": "https://docs.google.com/...",
       "pricing_calculator": "https://docs.google.com/..."
     }
   }
   ```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `aiir-sow-system/api/webhooks/google_drive_trigger.py` | Main webhook endpoint |
| `aiir-sow-system/test_webhook.py` | Test script to verify endpoint |
| `N8N_WEBHOOK_SETUP.md` | Detailed setup guide |
| `WEBHOOK_QUICKSTART.md` | This quick reference |
| `n8n_workflow_google_drive_webhook.json` | n8n workflow template |

---

## 🔍 Verification Checklist

- [ ] FastAPI server running on port 8000
- [ ] Test script passes all tests
- [ ] ngrok tunnel active and accessible
- [ ] n8n HTTP Request node configured with ngrok URL
- [ ] n8n workflow activated
- [ ] Test file added to Google Drive
- [ ] n8n execution shows success response
- [ ] New row appears in Tracker sheet
- [ ] New Calculator sheet created

---

## 🐛 Troubleshooting

### "Connection Refused"
→ Start FastAPI: `uvicorn api.index:app --reload --host 0.0.0.0 --port 8000`

### "404 Not Found"
→ Check URL in n8n is: `/webhooks/google-drive-file-added`

### "400 Bad Request"
→ n8n body should be: `{{ $json }}`

### ngrok "Not Found"
→ Restart ngrok, update n8n with new URL

### "500 Internal Server Error"
→ Check FastAPI logs for details

---

## 📊 Expected Response

```json
{
  "status": "success",
  "engagement_id": "ENG-20260319-ABC123",
  "file_urls": {
    "sow_template": "https://docs.google.com/document/d/...",
    "pricing_calculator": "https://docs.google.com/spreadsheets/d/..."
  },
  "file_info": {
    "file_id": "1a2b3c4d...",
    "filename": "transcript.txt",
    "mime_type": "text/plain"
  },
  "message": "File 'transcript.txt' processed successfully. Engagement ID: ENG-20260319-ABC123",
  "tracker_sheet_url": "https://docs.google.com/spreadsheets/d/..."
}
```

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| FastAPI Health | http://localhost:8000/health |
| Webhook Test | http://localhost:8000/webhooks/google-drive-file-added/test |
| Webhook Endpoint | http://localhost:8000/webhooks/google-drive-file-added |
| ngrok Inspector | http://127.0.0.1:4040 |

---

## 📚 Full Documentation

For detailed setup instructions, see:
- **N8N_WEBHOOK_SETUP.md** - Complete guide with screenshots
- **test_webhook.py** - Test all endpoints before connecting n8n
- **n8n_workflow_google_drive_webhook.json** - Import this into n8n

---

## ✅ Success Criteria

When everything works:
1. File added to Google Drive
2. n8n detects within 1 minute
3. n8n POSTs to FastAPI webhook
4. FastAPI processes file through Workflow 1
5. FastAPI returns success with URLs
6. Tracker sheet updated
7. Calculator sheet created
8. Rationale saved to Drive

**No polling. No delays. Instant processing.**

---

## 🎯 Next Steps

After setup works:

1. **Deploy to production** (see N8N_WEBHOOK_SETUP.md Part 6)
2. **Add authentication** (API keys, HMAC signatures)
3. **Monitor logs** (FastAPI, n8n, Google Drive)
4. **Set up alerts** (for failures)
5. **Scale** (handle multiple files simultaneously)

---

## 💡 Tips

- **Keep FastAPI and ngrok running** in separate terminals
- **Check ngrok inspector** (http://127.0.0.1:4040) to debug requests
- **Use test_webhook.py** before testing with real files
- **Monitor FastAPI logs** to see processing details
- **Free ngrok URLs change** when you restart - update n8n each time

---

## 🆘 Need Help?

1. Run test script: `python test_webhook.py`
2. Check FastAPI logs
3. Check ngrok inspector
4. Check n8n execution logs
5. Verify .env file has all required variables

Happy automating! 🚀
