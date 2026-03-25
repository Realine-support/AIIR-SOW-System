# AIIR SOW System - Quick Start Deployment Guide

**Ready to deploy?** Follow these steps in order.

---

## ⏱️ **Time Estimate: 1-2 Hours**

- OAuth2 Setup: 20-30 minutes
- Share Google Resources: 10 minutes
- Deploy to Vercel: 15-20 minutes
- Configure Environment Variables: 15-20 minutes
- Testing: 10-15 minutes

---

## 📋 **Before You Start**

**You need:**
- [ ] Access to `aline@aiirconsulting.com` Google account
- [ ] Access to Google Drive/Sheets with files to share
- [ ] Node.js installed (for Vercel CLI)
- [ ] Command line / terminal access

**You DON'T need:**
- ❌ Google Workspace admin access (using OAuth2 instead)
- ❌ Domain or hosting (using Vercel free tier)

---

## 🚀 **Step-by-Step (Do These In Order)**

### **STEP 1: Set Up OAuth2 for Gmail** (20-30 min)

**Why:** So system can send emails as `aline@aiirconsulting.com`

**Do this:**
1. Open: `OAUTH2_SETUP_GUIDE.md`
2. Follow ALL steps (1-4)
3. Test that OAuth2 works locally

**Result:**
- ✅ You have 4 new environment variables in `.env`
- ✅ Test email sent successfully

**Don't skip this!** Emails won't work without OAuth2 setup.

---

### **STEP 2: Share Google Resources** (10 min)

**Why:** Service account needs permission to access Drive/Sheets/Docs

**Do this:**

**Service Account Email:** `aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com`

**Share these as "Editor":**
1. Tracker Sheet: https://docs.google.com/spreadsheets/d/1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM
2. Transcripts Folder (Google Drive ID: `1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu`)
3. Rationales Folder (ID: `1IFEtmm73v3QkCfploTrt5ox9rn898kra`)
4. SOW Templates Folder (ID: `19oUtBCmaxEhwQWtxKJ1EZS_VIRf5Clwm`)
5. Archive Folder (ID: `1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu`)
6. Client Master Folder (ID: `1wiW8A9j7BTavRObjrXFQan2mMv1ElaS2`)

**Share as "Viewer":**
7. SOW Template Doc (ID: `1HRZ_1qPl9DiCymAZE9H-xpRy-shTXphw`)

**How to share:**
- Open each resource → Click "Share"
- Paste service account email
- Set role (Editor or Viewer)
- Uncheck "Notify people"
- Click "Share"

---

### **STEP 3: Install Vercel CLI** (5 min)

**Check if Node.js is installed:**
```bash
node --version
```

**If not installed:**
- Download: https://nodejs.org/en/download/
- Install LTS version
- Restart terminal

**Install Vercel CLI:**
```bash
npm install -g vercel
```

**Login to Vercel:**
```bash
vercel login
```
(Browser opens → Sign in with GitHub/Email)

---

### **STEP 4: Deploy to Vercel** (10 min)

```bash
cd d:\AIIR\aiir-sow-system
vercel deploy --prod
```

**Answer prompts:**
- Set up and deploy? **Y**
- Which scope? **Your username**
- Link to existing project? **N**
- Project name? **aiir-sow-system**
- Directory? **./` (just press Enter)

**Wait 2-3 minutes for deployment...**

**Copy your URL:**
```
✅ Production: https://aiir-sow-system-XXXXX.vercel.app
```

**SAVE THIS URL!** You'll need it in Step 5.

---

### **STEP 5: Add Environment Variables to Vercel** (15-20 min)

**Go to:**
https://vercel.com/dashboard → Click your project → Settings → Environment Variables

**Add ALL these variables** (copy from your `.env` file):

**Essential Variables (26 total):**

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-Ac-tHKDt...

# Google Credentials (see note below)
GOOGLE_CREDENTIALS_PATH=/var/task/google-credentials.json
GOOGLE_SERVICE_ACCOUNT_EMAIL=aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com

# Google Resource IDs
TRACKER_SHEET_ID=1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM
TRACKER_TAB_NAME=Tracker
CALCULATOR_SHEET_ID=1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM
CALCULATOR_TAB_NAME=Calculator
TRANSCRIPTS_FOLDER_ID=1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu
RATIONALES_FOLDER_ID=1IFEtmm73v3QkCfploTrt5ox9rn898kra
SOW_TEMPLATES_FOLDER_ID=19oUtBCmaxEhwQWtxKJ1EZS_VIRf5Clwm
SOW_TEMPLATE_DOC_ID=1HRZ_1qPl9DiCymAZE9H-xpRy-shTXphw
CLIENT_MASTER_FOLDER_ID=1wiW8A9j7BTavRObjrXFQan2mMv1ElaS2
ARCHIVE_FOLDER_ID=1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu

# Email Configuration
GMAIL_SEND_AS=aline@aiirconsulting.com
REVIEW_EMAIL_TO=kapurkartanmay@gmail.com
CLIENT_EMAIL_FROM=aline@aiirconsulting.com

# Gmail OAuth2 (from Step 1)
GMAIL_USE_OAUTH2=true
GMAIL_REFRESH_TOKEN=1//0xxxxxxxx... (from oauth setup)
GMAIL_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxx

# Redis
UPSTASH_REDIS_REST_URL=https://select-porpoise-69103.upstash.io
UPSTASH_REDIS_REST_TOKEN=(your token from .env)

# Webhook URLs (USE YOUR VERCEL URL from Step 4!)
BASE_URL=https://aiir-sow-system-XXXXX.vercel.app
APPROVE_PRICING_WEBHOOK_URL=https://aiir-sow-system-XXXXX.vercel.app/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=https://aiir-sow-system-XXXXX.vercel.app/webhooks/approve-sow

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
```

**IMPORTANT - Google Credentials JSON:**

You need to upload the service account JSON file content. Create one more variable:

```bash
Name: GOOGLE_CREDENTIALS_JSON
Value: (paste ENTIRE content of sales-ai-agent-484003-fcd77f3c1a42.json)
```

**OR convert to base64:**
```bash
cd d:\AIIR
python -c "import base64; f=open('sales-ai-agent-484003-fcd77f3c1a42.json','rb'); print(base64.b64encode(f.read()).decode())"
```

Then add:
```bash
Name: GOOGLE_CREDENTIALS_BASE64
Value: (paste base64 output)
```

---

### **STEP 6: Update Code for Vercel Credentials** (5 min)

**The code needs to read Google credentials from environment variable instead of file.**

**I'll create a helper function for this - let me do that now...**

Actually, let's test first and see if there's an error, then fix if needed.

---

### **STEP 7: Test Deployment** (5 min)

**Test health endpoint:**
```bash
curl https://aiir-sow-system-XXXXX.vercel.app/
```

**Expected:**
```json
{"status":"healthy","service":"AIIR SOW Automation System"}
```

**Test cron endpoint:**
```bash
curl https://aiir-sow-system-XXXXX.vercel.app/cron/watch-transcripts
```

**Expected:**
```json
{"message":"Processed 0 files","total_files":0,...}
```

**Check logs in Vercel:**
- Dashboard → Functions → Logs
- Look for errors
- If you see credentials error, we'll fix it

---

### **STEP 8: Upload Test Transcript** (5 min)

**Create file:** `test-transcript.txt`

```
Client Company: Tanmay Kapurkar
Decision Maker: kapurkartanmay@gmail.com
Decision Maker Name: Tanmay Kapurkar
Coachee Name: Tanmay Kapurkar
Seniority: C-Suite
Duration: 16 weeks
Market Type: Hybrid

Transcript:
This is a test engagement for Tanmay Kapurkar. He's looking to improve his
self-awareness and executive presence as a C-Suite leader.

The conversation highlighted interest in understanding stakeholder perception and
developing stronger influence. He mentioned wanting honest feedback about blind
spots in his leadership approach.

Budget for this engagement is approximately $25,000. Looking to start within 2 weeks.
```

**Upload to Google Drive:**
1. Go to Transcripts folder: https://drive.google.com/drive/folders/1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu
2. Upload `test-transcript.txt`
3. Wait 5 minutes (cron runs every 5 min)

**OR trigger manually:**
```bash
curl https://aiir-sow-system-XXXXX.vercel.app/cron/watch-transcripts
```

---

### **STEP 9: Verify Workflow** (10 min)

**Check Email #1 (Pricing Review):**
- Check: `kapurkartanmay@gmail.com`
- FROM: `aline@aiirconsulting.com`
- SUBJECT: "Review Pricing: Tanmay Kapurkar - Tanmay Kapurkar"
- Click: **"Approve Pricing"**

**Check Email #2 (SOW Review):**
- Check: `kapurkartanmay@gmail.com` (within 30 sec)
- FROM: `aline@aiirconsulting.com`
- SUBJECT: "Review SOW: Tanmay Kapurkar - Tanmay Kapurkar"
- Click link to view SOW
- Click: **"Approve & Send to Client"**

**Check Email #3 (Client SOW):**
- Check: `kapurkartanmay@gmail.com` (within 30 sec)
- FROM: `aline@aiirconsulting.com`
- SUBJECT: "Statement of Work - Tanmay Kapurkar"
- ATTACHMENT: SOW PDF

**Check Google Sheets:**
- Tracker: New row with status "completed"
- Calculator: Pricing breakdown

**Check Google Drive:**
- Archive folder: Transcript moved
- Rationales folder: Rationale document

---

## ✅ **Success Checklist**

- [ ] OAuth2 set up and tested locally
- [ ] All 7 Google resources shared with service account
- [ ] Vercel CLI installed and logged in
- [ ] Deployed to Vercel successfully
- [ ] All ~26 environment variables added to Vercel
- [ ] Health endpoint returns "healthy"
- [ ] Cron endpoint returns "Processed X files"
- [ ] Test transcript uploaded
- [ ] Received Email #1 (pricing review)
- [ ] Received Email #2 (SOW review)
- [ ] Received Email #3 (client SOW with PDF)
- [ ] Tracker sheet updated to "completed"
- [ ] Transcript moved to Archive

**If all checked:** 🎉 **SYSTEM IS WORKING!**

---

## ❌ **If Something Doesn't Work**

### **No emails received:**
- Check Vercel logs for errors
- Verify OAuth2 variables in Vercel
- Check `GMAIL_USE_OAUTH2=true`
- Re-run OAuth setup if token expired

### **403 Forbidden errors (Google APIs):**
- Verify service account has access to all resources
- Check all folder IDs are correct
- Share resources as "Editor" (not "Viewer")

### **Cron not running:**
- Vercel cron runs every 5 minutes
- Or trigger manually with curl command
- Check Vercel dashboard → Cron Jobs

### **500 errors:**
- Check Vercel logs for stack trace
- Verify all environment variables are set
- Check Google credentials JSON is in env vars

---

## 📚 **Detailed Guides**

For more details, see:
- **OAuth2 Setup:** `OAUTH2_SETUP_GUIDE.md`
- **Full Deployment:** `DEPLOYMENT_GUIDE_YOUR_SETUP.md`
- **Troubleshooting:** `DEPLOYMENT_CHECKLIST.md`

---

## 🎯 **What's Next?**

**After successful testing:**
1. Upload real transcripts to test with actual clients
2. Monitor for 1-2 weeks
3. Refresh OAuth2 token when it expires (~7 days)
4. Consider getting workspace admin to set up delegation (permanent solution)

---

**Last Updated:** March 12, 2026
**Status:** Ready for deployment ✅
**Your Setup:** OAuth2 authentication (Option 2)
