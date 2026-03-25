# 🚀 AIIR SOW System - Deployment Checklist

Complete this checklist before deploying to production on Railway.

---

## 📋 Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **Copy `.env.example` to `.env`**
  ```bash
  cd aiir-sow-system
  cp .env.example .env
  ```

- [ ] **Fill in all required environment variables:**
  - [ ] `OPENAI_API_KEY` - OpenAI API key
  - [ ] `GOOGLE_SERVICE_ACCOUNT_EMAIL` - Google service account email
  - [ ] `GOOGLE_CREDENTIALS_PATH` - Path to service account JSON (local only)
  - [ ] `TRACKER_SHEET_ID` - Google Sheets tracker ID
  - [ ] `CALCULATOR_SHEET_ID` - Google Sheets calculator ID
  - [ ] `SHARED_DRIVE_ID` - Google Shared Drive ID
  - [ ] `CALCULATOR_TEMPLATE_ID` - Calculator template ID
  - [ ] `SOW_TEMPLATE_DOC_ID` - SOW template document ID
  - [ ] All folder IDs (transcripts, rationales, SOW templates, etc.)
  - [ ] Email configuration (Gmail send as, review email, etc.)
  - [ ] `UPSTASH_REDIS_REST_URL` - Upstash Redis URL
  - [ ] `UPSTASH_REDIS_REST_TOKEN` - Upstash Redis token

### 2. Google Cloud Setup

- [ ] **Create Google Cloud service account**
  - [ ] Enable Google Drive API
  - [ ] Enable Google Sheets API
  - [ ] Enable Google Docs API
  - [ ] Enable Gmail API (if sending emails)

- [ ] **Download service account JSON key**
  - [ ] Place in project root for local testing
  - [ ] Convert to single-line JSON for Railway:
    ```bash
    cat service-account.json | jq -c
    ```

- [ ] **Grant service account access:**
  - [ ] Share Google Drive folders with service account email
  - [ ] Share tracker sheet with service account (Editor access)
  - [ ] Share calculator sheet with service account (Editor access)
  - [ ] Share template documents with service account

### 3. Upstash Redis Setup

- [ ] **Create Upstash Redis database** (free tier works)
  - [ ] Copy REST URL
  - [ ] Copy REST token
  - [ ] Add to environment variables

### 4. Local Testing

- [ ] **Install dependencies:**
  ```bash
  cd aiir-sow-system
  pip install -r requirements.txt
  ```

- [ ] **Start local server:**
  ```bash
  python -m uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
  ```

- [ ] **Test endpoints:**
  - [ ] Visit http://localhost:8000/docs (API documentation)
  - [ ] Visit http://localhost:8000/health (basic health check)
  - [ ] Visit http://localhost:8000/health/detailed (dependency verification)
  - [ ] Visit http://localhost:8000/health/live (liveness probe)
  - [ ] Visit http://localhost:8000/health/ready (readiness probe)

- [ ] **Run manual tests:**
  ```bash
  python test_webhook.py
  python test_business_logic.py
  ```

- [ ] **Verify all tests pass locally**

### 5. GitHub Setup

- [ ] **Push latest code to GitHub:**
  ```bash
  git add .
  git commit -m "Production-ready deployment"
  git push origin master
  ```

- [ ] **Verify all files are committed:**
  - [ ] `Dockerfile`
  - [ ] `railway.toml`
  - [ ] `.gitignore`
  - [ ] `aiir-sow-system/` folder with all code
  - [ ] `README.md`
  - [ ] `.env.example`
  - [ ] `DEPLOYMENT_CHECKLIST.md`

---

## 🚂 Railway Deployment

### 1. Delete Old Service (If Exists)

- [ ] **Clear Railway cache by deleting old service:**
  - [ ] Go to Railway Dashboard
  - [ ] Select old service
  - [ ] Settings → Danger → Delete Service
  - [ ] Confirm deletion

### 2. Create New Railway Service

- [ ] **Create new Railway project:**
  - [ ] Click "New Project"
  - [ ] Select "Deploy from GitHub repo"
  - [ ] Choose repository: `Realine-support/AIIR-SOW-System`
  - [ ] Railway auto-detects Dockerfile ✅

### 3. Configure Environment Variables

- [ ] **Add ALL environment variables from `.env.example`:**

**CRITICAL: Google Credentials**
- [ ] Convert service account JSON to single-line string:
  ```bash
  cat service-account.json | jq -c
  ```
- [ ] Add to Railway as `GOOGLE_CREDENTIALS_JSON` (not file path!)

**Production Configuration:**
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `LOG_LEVEL=INFO`
- [ ] `BASE_URL=https://your-app.railway.app` (replace with actual Railway URL)

**All other variables from `.env.example`:**
- [ ] Copy each variable from `.env.example`
- [ ] Paste into Railway Variables tab
- [ ] Verify all 25+ variables are set

### 4. Deploy

- [ ] **Trigger deployment:**
  - Railway auto-deploys on git push
  - Monitor build logs in Railway Dashboard
  - Wait for build to complete (~3-5 minutes)

- [ ] **Check deployment status:**
  - [ ] Build succeeded
  - [ ] Service is running
  - [ ] No errors in logs

### 5. Verify Deployment

- [ ] **Copy Railway deployment URL**
  - Example: `https://aiir-sow-system-production.up.railway.app`

- [ ] **Run verification script:**
  ```bash
  python verify_deployment.py https://your-app.railway.app
  ```

- [ ] **Manual endpoint checks:**
  - [ ] Visit `https://your-app.railway.app/health`
  - [ ] Visit `https://your-app.railway.app/health/detailed`
  - [ ] Visit `https://your-app.railway.app/docs`

- [ ] **Verify health check response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-03-26T...",
    "environment": "production",
    "dependencies": {
      "openai": {"status": "healthy"},
      "google_apis": {"status": "healthy"},
      "redis": {"status": "healthy"}
    }
  }
  ```

### 6. Configure n8n Webhooks

- [ ] **Update n8n workflow webhook URLs:**
  - [ ] Replace `http://localhost:8000` with Railway URL
  - [ ] Test webhook: `/webhooks/google-drive-file-added`
  - [ ] Test webhook: `/webhooks/pricing-model-approved`
  - [ ] Test webhook: `/webhooks/approve-pricing`
  - [ ] Test webhook: `/webhooks/approve-sow`

- [ ] **Verify n8n workflows:**
  - [ ] Google Drive watch trigger
  - [ ] Pricing approval workflow
  - [ ] SOW approval workflow
  - [ ] Client delivery workflow

---

## ✅ Post-Deployment Verification

### End-to-End Testing

- [ ] **Upload test transcript to Google Drive:**
  - [ ] Verify transcript processing triggered
  - [ ] Check tracker sheet updated
  - [ ] Verify pricing calculator created
  - [ ] Confirm approval email sent

- [ ] **Test pricing approval:**
  - [ ] Click approval link in email
  - [ ] Verify SOW generation triggered
  - [ ] Check SOW document created
  - [ ] Confirm SOW approval email sent

- [ ] **Test SOW approval:**
  - [ ] Click approval link in email
  - [ ] Verify client documents created
  - [ ] Check files moved to client folder
  - [ ] Confirm client email sent

- [ ] **Verify all documents:**
  - [ ] Pricing calculator with correct data
  - [ ] SOW document with filled variables
  - [ ] Files in correct folders
  - [ ] Tracker sheet updated correctly

### Monitoring

- [ ] **Set up Railway monitoring:**
  - [ ] Check Railway logs for errors
  - [ ] Monitor resource usage
  - [ ] Set up alerts (optional)

- [ ] **Test health checks:**
  - [ ] Liveness probe: `/health/live`
  - [ ] Readiness probe: `/health/ready`
  - [ ] Detailed health: `/health/detailed`

---

## 🔒 Security Review

- [ ] **Environment variables secure:**
  - [ ] No secrets in git history
  - [ ] All secrets in Railway environment variables
  - [ ] `.env` file in `.gitignore`

- [ ] **CORS configured correctly:**
  - [ ] Production mode restricts origins
  - [ ] Only n8n domain whitelisted

- [ ] **Google permissions minimal:**
  - [ ] Service account only has required permissions
  - [ ] Shared Drive access limited

---

## 📊 Success Criteria

Your deployment is successful when:

- ✅ All health checks return `status: healthy`
- ✅ Verification script passes all tests
- ✅ End-to-end workflow completes successfully
- ✅ No errors in Railway logs
- ✅ n8n webhooks connecting successfully
- ✅ Documents generated correctly
- ✅ Emails sent and received

---

## 🚨 Troubleshooting

### Build Fails

**Error: pydantic build error**
- Solution: Delete Railway service, create fresh (clears cache)
- Verify: `requirements.txt` has `pydantic==2.8.0`

**Error: Python version mismatch**
- Solution: Dockerfile explicitly uses Python 3.11.9
- Verify: `Dockerfile` base image is `python:3.11.9-slim`

### Health Checks Fail

**Error: OpenAI API unhealthy**
- Check: `OPENAI_API_KEY` is valid
- Check: OpenAI API is not rate limited

**Error: Google APIs unhealthy**
- Check: `GOOGLE_CREDENTIALS_JSON` is valid single-line JSON
- Check: Service account has correct permissions
- Check: APIs are enabled in Google Cloud Console

**Error: Redis unhealthy**
- Check: `UPSTASH_REDIS_REST_URL` is correct
- Check: `UPSTASH_REDIS_REST_TOKEN` is valid
- Check: Upstash Redis database is active

### Webhooks Not Working

**Error: n8n can't reach webhooks**
- Check: `BASE_URL` is correct Railway URL
- Check: Railway service is running
- Check: CORS allows n8n domain

---

## 📞 Support

If issues persist:
1. Check Railway deployment logs
2. Review troubleshooting section in [README.md](README.md)
3. Create GitHub issue with error logs

---

**Deployment Ready Score: __/100**

Count checkboxes completed, then run:
```bash
python verify_deployment.py https://your-app.railway.app
```

✅ All tests pass = **100/100 - Ready for Production!**
