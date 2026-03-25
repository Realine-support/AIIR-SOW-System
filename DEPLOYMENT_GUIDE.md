# AIIR SOW System - Deployment Guide

**Date:** March 12, 2026
**Version:** 1.0.0 (Complete)
**Status:** ✅ Ready for Deployment

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Vercel account (free tier is sufficient)
- ✅ All Google Cloud credentials configured
- ✅ OpenAI API key
- ✅ Upstash Redis account
- ✅ All environment variables ready (see `.env` file)

---

## Local Testing (Optional but Recommended)

### 1. Test the Application Locally

```bash
cd d:/AIIR/aiir-sow-system

# Activate virtual environment
venv\Scripts\activate

# Run the FastAPI server
uvicorn api.index:app --reload --port 8000
```

### 2. Test Endpoints

Open your browser and test:

- **Health check:** http://localhost:8000/
- **API docs:** http://localhost:8000/docs
- **Cron endpoint (manual trigger):** http://localhost:8000/cron/watch-transcripts

### 3. Test Business Logic (Already Done)

```bash
python test_business_logic.py
```

All 4 test cases should pass ✅

---

## Deployment to Vercel

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

### Step 3: Deploy to Vercel

Navigate to project directory:

```bash
cd d:/AIIR/aiir-sow-system
```

Deploy:

```bash
vercel deploy --prod
```

The CLI will:
1. Detect the project
2. Ask for project name (use `aiir-sow-system`)
3. Build and deploy
4. Return your production URL (e.g., `https://aiir-sow-system.vercel.app`)

### Step 4: Configure Environment Variables in Vercel

**CRITICAL:** You must add all environment variables to Vercel.

Go to your Vercel dashboard:
1. Select your project (`aiir-sow-system`)
2. Go to **Settings** → **Environment Variables**
3. Add each variable from your `.env` file:

#### Required Environment Variables:

```
OPENAI_API_KEY=sk-proj-Ac-tHKDt6ZWGgxT QN7-40WDjNbM1A7A6K_G57IQTqKZWOPXb07Z07rFuchT9Qn77Z4VphbzzBlT3BlbkFJ_NsWF060WYfZqfkai3YJGgyxFMkXEH94kpfmFEmCOQHwfbAKijbXBmCLuOdrmxHfPjozJapEYA

GOOGLE_CREDENTIALS_PATH=./google-credentials.json

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

GMAIL_SEND_AS=kapurkartanmay@gmail.com
REVIEW_EMAIL_TO=kapurkartanmay@gmail.com
CLIENT_EMAIL_FROM=kapurkartanmay@gmail.com

UPSTASH_REDIS_REST_URL=https://select-porpoise-69103.upstash.io
UPSTASH_REDIS_REST_TOKEN=gQAAAAAAAQ3vAAIncDEzMzViNjljZmEyMDc0NzdkOTQ3YmFhZmY5YTlmM2Y4MnAxNjkxMDM

BASE_URL=https://YOUR-VERCEL-URL.vercel.app
APPROVE_PRICING_WEBHOOK_URL=${BASE_URL}/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=${BASE_URL}/webhooks/approve-sow

ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
```

**Important:** Replace `YOUR-VERCEL-URL` with your actual Vercel URL after deployment.

### Step 5: Upload Google Credentials JSON

The Google service account JSON file needs to be accessible:

**Option A: Environment Variable (Recommended for Vercel)**

Convert the JSON file to a single-line string and add as environment variable:

```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"sales-ai-agent-484003",...}
```

Then update `app/config.py` to read from this variable if `GOOGLE_CREDENTIALS_PATH` doesn't exist.

**Option B: Include in Deployment**

Copy the JSON file to the project root and ensure it's not in `.gitignore` for deployment only.

### Step 6: Verify Cron Job is Configured

After deployment, check Vercel dashboard:
1. Go to **Settings** → **Cron Jobs**
2. Verify you see: `/cron/watch-transcripts` running every 5 minutes (`*/5 * * * *`)

If not, Vercel should have auto-configured it from `vercel.json`.

### Step 7: Test Production Deployment

Test your production endpoints:

1. **Health check:** `https://YOUR-URL.vercel.app/`
2. **API docs:** `https://YOUR-URL.vercel.app/docs`
3. **Manual cron trigger (for testing):** `https://YOUR-URL.vercel.app/cron/watch-transcripts`

---

## Post-Deployment Configuration

### 1. Update Webhook URLs

After getting your production URL, update the environment variables in Vercel:

```
BASE_URL=https://aiir-sow-system.vercel.app
APPROVE_PRICING_WEBHOOK_URL=https://aiir-sow-system.vercel.app/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=https://aiir-sow-system.vercel.app/webhooks/approve-sow
```

Then redeploy:

```bash
vercel deploy --prod
```

### 2. Grant Google Service Account Access

Make sure the service account email has access to all Google resources:

**Service Account Email:** `aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com`

**Grant access to:**
- ✅ Tracker Sheet (Editor)
- ✅ All Google Drive folders (Editor)
- ✅ SOW Template document (Viewer)

### 3. Configure Gmail Delegation (if using Gmail API)

For the service account to send emails as `kapurkartanmay@gmail.com`, you need domain-wide delegation:

1. Go to Google Workspace Admin Console
2. Navigate to **Security** → **API Controls** → **Domain-wide Delegation**
3. Add the service account client ID with scopes:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/spreadsheets`

**Alternative:** Use OAuth2 for Gmail (requires manual token refresh).

---

## Testing the Complete System

### Test Workflow 1: Transcript → Pricing

1. Upload a test transcript to the Transcripts folder
2. Wait 5 minutes (or manually trigger cron: `/cron/watch-transcripts`)
3. Check logs in Vercel dashboard
4. You should receive a pricing review email
5. Click "Approve Pricing" in the email

### Test Workflow 2: SOW Generation

1. After approving pricing, wait for SOW generation
2. You should receive an SOW review email
3. Click the SOW URL to review
4. Click "Approve & Send to Client"

### Test Workflow 3: Send & Archive

1. After approving SOW, the system should:
   - Send SOW PDF to client email
   - Archive the transcript
   - Update Tracker status to "completed"

### Verify in Google Sheets

Check the Tracker sheet:
- New row with engagement ID
- All fields populated
- Rationale URL working
- SOW URL working
- Status = "completed"

---

## Monitoring & Logs

### View Logs in Vercel

1. Go to Vercel dashboard
2. Select your project
3. Click **Deployments** → [Latest Deployment] → **Logs**
4. Filter by function:
   - `/cron/watch-transcripts` - Cron job logs
   - `/webhooks/approve-pricing` - Pricing approval logs
   - `/webhooks/approve-sow` - SOW approval logs

### Monitor Upstash Redis

1. Go to Upstash dashboard
2. Select your Redis database
3. Use **Data Browser** to see keys:
   - `engagement:*:state` - Workflow states
   - `processing:*` - File processing status

---

## Troubleshooting

### Issue: Cron job not running

**Solution:**
- Check Vercel dashboard → Settings → Cron Jobs
- Ensure cron schedule is: `*/5 * * * *`
- Manually trigger: `https://YOUR-URL.vercel.app/cron/watch-transcripts`

### Issue: Google API authentication errors

**Solution:**
- Verify service account JSON is correctly uploaded
- Check service account has access to all folders/sheets
- Verify API scopes in domain-wide delegation

### Issue: Emails not sending

**Solution:**
- Check Gmail delegation is configured
- Verify `GMAIL_SEND_AS` matches delegated email
- Check Gmail API is enabled in Google Cloud Console

### Issue: OpenAI extraction failing

**Solution:**
- Verify OpenAI API key is correct
- Check API quota/usage limits
- Review error logs for specific failures

### Issue: Webhook buttons not working

**Solution:**
- Ensure `BASE_URL` is set to production Vercel URL
- Verify webhook URLs are correct in environment variables
- Check CORS settings in FastAPI app

---

## Scaling Considerations

### Free Tier Limits

**Vercel (Free Tier):**
- 100 GB-hours compute time/month
- 100 GB bandwidth/month
- Serverless function timeout: 10 seconds
- ✅ Sufficient for ~100-200 transcripts/month

**Upstash Redis (Free Tier):**
- 10,000 commands/day
- 256 MB storage
- ✅ Sufficient for current usage

**OpenAI:**
- Pay-per-use (~$0.01-0.02 per transcript)
- No free tier
- ✅ Budget ~$50/month for 2,500-5,000 extractions

### If You Need to Scale

1. **Upgrade Vercel to Pro** ($20/month)
   - 1,000 GB-hours compute
   - 1 TB bandwidth
   - 60-second function timeout

2. **Upgrade Upstash** ($10/month)
   - 100,000 commands/day
   - 1 GB storage

3. **Optimize OpenAI Costs**
   - Use GPT-4o-mini for non-critical extractions
   - Implement caching for similar transcripts

---

## Backup & Disaster Recovery

### Data Backup

All data is stored in Google Sheets/Drive:
- **Tracker Sheet:** Primary source of truth
- **Google Drive:** All documents preserved
- **Redis:** Temporary state only (not critical)

**Recommendation:** Set up Google Workspace automated backups.

### System Recovery

If Vercel deployment fails:
1. All data is preserved in Google Sheets/Drive
2. Redeploy from GitHub/local code
3. Re-configure environment variables
4. System resumes from last state

---

## Maintenance

### Weekly

- Review Tracker sheet for "failed" or "manual_review" statuses
- Check Vercel logs for errors
- Monitor OpenAI API usage

### Monthly

- Review and clean up old Redis keys (auto-expire after 24 hours)
- Archive old transcripts
- Review pricing accuracy vs. manual SOWs

### Quarterly

- Update OpenAI model if new versions available
- Review business logic for changes
- Update tier defaults if pricing changes

---

## Security Best Practices

1. **Never commit `.env` or credentials to Git** ✅ (already in `.gitignore`)
2. **Rotate API keys quarterly**
3. **Use environment-specific configs** (dev vs. prod)
4. **Monitor webhook access logs** for suspicious activity
5. **Enable 2FA on all accounts** (Vercel, Google, OpenAI, Upstash)

---

## Support & Documentation

**Project Files:**
- [README.md](aiir-sow-system/README.md) - Project overview
- [BUSINESS_LOGIC_ANALYSIS.md](BUSINESS_LOGIC_ANALYSIS.md) - Requirements
- [TEST_RESULTS_ANALYSIS.md](TEST_RESULTS_ANALYSIS.md) - Test results
- [IMPLEMENTATION_COMPLETE_PHASE_1_2.md](IMPLEMENTATION_COMPLETE_PHASE_1_2.md) - Build status

**APIs Used:**
- [Google Drive API](https://developers.google.com/drive/api/v3/about-sdk)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Google Docs API](https://developers.google.com/docs/api)
- [Gmail API](https://developers.google.com/gmail/api)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Upstash Redis](https://docs.upstash.com/redis)

**Contact:**
- Email: kapurkartanmay@gmail.com
- Developer: Claude (Anthropic AI)

---

## Deployment Checklist

Before going to production:

- [ ] All environment variables configured in Vercel
- [ ] Google service account has access to all resources
- [ ] Gmail delegation configured (if using Gmail API)
- [ ] Cron job verified in Vercel dashboard
- [ ] Webhook URLs updated with production domain
- [ ] Test transcript uploaded and processed successfully
- [ ] Pricing review email received and functional
- [ ] SOW generation tested and functional
- [ ] Client email delivery tested
- [ ] Monitoring set up (logs, Redis, Sheets)

---

**Ready to Deploy!** 🚀

Follow the steps above to deploy the AIIR SOW System to production.
