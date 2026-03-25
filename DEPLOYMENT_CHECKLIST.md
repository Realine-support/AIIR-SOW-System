# AIIR SOW System - Deployment Checklist

**Status:** Not Yet Deployed (Local Only)

---

## 🚨 **CRITICAL: System Cannot Run Locally**

The system **MUST** be deployed to Vercel to work because:
- ✅ Cron jobs need Vercel's scheduler (runs every 5 minutes)
- ✅ Webhooks need public URLs (for email approval buttons)
- ✅ Serverless functions need to be hosted 24/7

**You cannot test the full workflow until deployed.**

---

## 📋 **Pre-Deployment Checklist**

### **Step 1: Fix Gmail Email Sending** ⚠️ BLOCKER

**Current Issue:**
- Service account (`aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com`) cannot send emails
- Need to configure one of these options:

**Choose ONE option below:**

#### **Option A: Use Resend (EASIEST - Recommended)** ✅

**Why:**
- Simple 5-minute setup
- Free tier: 3,000 emails/month
- No Gmail complexity
- Most reliable

**Steps:**
1. Go to https://resend.com/signup
2. Create free account
3. Get API key
4. Add domain verification (or use onboarding domain for testing)
5. Update `.env`:
   ```bash
   # Replace Gmail with Resend
   RESEND_API_KEY=re_xxxxxxxxxxxxx
   RESEND_FROM_EMAIL=onboarding@resend.dev  # or your@domain.com
   REVIEW_EMAIL_TO=kapurkartanmay@gmail.com
   ```
6. Update code to use Resend instead of Gmail API

**Time:** 10 minutes
**Complexity:** ⭐ (Very Easy)

---

#### **Option B: Gmail OAuth2 (For Testing)** ⚙️

**Why:**
- Works with regular Gmail accounts
- No domain-wide delegation needed
- Good for testing

**Downside:**
- Token expires every 7 days
- Manual refresh needed
- More complex setup

**Steps:**
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download credentials JSON
4. Run OAuth flow to get refresh token:
   ```bash
   # I can create a script for this
   python get_gmail_token.py
   ```
5. Copy refresh token to `.env`:
   ```bash
   GMAIL_REFRESH_TOKEN=xxxxxxxxxxxxx
   GMAIL_CLIENT_ID=xxxxxxxxxxxxx
   GMAIL_CLIENT_SECRET=xxxxxxxxxxxxx
   ```
6. Update `gmail_service.py` to use OAuth2 instead of service account

**Time:** 30-45 minutes
**Complexity:** ⭐⭐⭐ (Medium)

---

#### **Option C: Google Workspace Domain-Wide Delegation** 🏢

**Why:**
- Best for production
- Service account can send as any user
- No token expiration

**Requirements:**
- `kapurkartanmay@gmail.com` MUST be a Google Workspace account (NOT regular Gmail)
- You MUST have Google Workspace Admin access

**Steps:**
1. Go to Google Workspace Admin Console (admin.google.com)
2. Security → Access and data control → API Controls
3. Domain-wide Delegation → Add new
4. Client ID: (from service account JSON)
5. OAuth Scopes: `https://www.googleapis.com/auth/gmail.send`
6. Current code should work after this

**Time:** 15 minutes (if you have admin access)
**Complexity:** ⭐⭐ (Easy if you're admin, impossible if not)

---

### **Step 2: Share Google Resources** ⚠️ REQUIRED

**Grant service account access to all Google Drive/Sheets/Docs:**

Service Account Email: `aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com`

**Share these resources (click Share button, add email, set to "Editor"):**

- [ ] Tracker Sheet: https://docs.google.com/spreadsheets/d/1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM
- [ ] Calculator Sheet: (same as Tracker, different tab)
- [ ] Transcripts Folder: ID `1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu`
- [ ] Rationales Folder: ID `1IFEtmm73v3QkCfploTrt5ox9rn898kra`
- [ ] SOW Templates Folder: ID `19oUtBCmaxEhwQWtxKJ1EZS_VIRf5Clwm`
- [ ] Archive Folder: ID `1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu` (same as Transcripts)
- [ ] Client Master Folder: ID `1wiW8A9j7BTavRObjrXFQan2mMv1ElaS2`

**Share this as "Viewer" only:**
- [ ] SOW Template Doc: ID `1HRZ_1qPl9DiCymAZE9H-xpRy-shTXphw`

**How to share:**
1. Open each resource in Google Drive/Sheets
2. Click "Share" button (top right)
3. Paste: `aiir-sow-automation@sales-ai-agent-484003.iam.gserviceaccount.com`
4. Set role to "Editor" (or "Viewer" for template)
5. Uncheck "Notify people"
6. Click "Share"

**Time:** 10 minutes
**Complexity:** ⭐ (Very Easy)

---

### **Step 3: Deploy to Vercel** 🚀 REQUIRED

**Install Vercel CLI:**
```bash
npm install -g vercel
```

**Login to Vercel:**
```bash
vercel login
```
- Opens browser, sign in with GitHub/GitLab/Email

**Deploy:**
```bash
cd d:\AIIR\aiir-sow-system
vercel deploy --prod
```

**Follow prompts:**
- Link to existing project? → No
- Project name? → aiir-sow-system
- Directory? → ./ (current directory)
- Build settings? → Accept defaults

**Wait for deployment (~2-3 minutes)**

**Get your URL:**
```
✅ Production: https://aiir-sow-system-xxxxx.vercel.app
```

**Time:** 10 minutes
**Complexity:** ⭐⭐ (Easy)

---

### **Step 4: Configure Environment Variables in Vercel** ⚙️ REQUIRED

**Go to Vercel Dashboard:**
1. https://vercel.com/dashboard
2. Click your project: `aiir-sow-system`
3. Settings → Environment Variables

**Add ALL 47 variables from `.env` file:**

**Copy these from your `.env`:**
```bash
OPENAI_API_KEY=sk-proj-Ac-tHKDt6ZWGgxT...
GOOGLE_CREDENTIALS_PATH=/var/task/sales-ai-agent-484003-fcd77f3c1a42.json
TRACKER_SHEET_ID=1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM
... (all 47 variables)
```

**IMPORTANT:** Update these after deployment:
```bash
BASE_URL=https://aiir-sow-system-xxxxx.vercel.app  # Your actual Vercel URL
APPROVE_PRICING_WEBHOOK_URL=https://aiir-sow-system-xxxxx.vercel.app/webhooks/approve-pricing
APPROVE_SOW_WEBHOOK_URL=https://aiir-sow-system-xxxxx.vercel.app/webhooks/approve-sow
```

**Special Note for Google Credentials:**
- Vercel doesn't support file uploads directly
- You need to encode the JSON as base64 OR use environment variable
- **Option 1:** Set `GOOGLE_CREDENTIALS_JSON` with full JSON content
- **Option 2:** Upload to Vercel Storage (paid feature)
- **Option 3:** Use base64 encoding (I can help with this)

**Time:** 15 minutes
**Complexity:** ⭐⭐ (Medium - lots of copy/paste)

---

### **Step 5: Test Deployment** 🧪

**Test health endpoint:**
```bash
curl https://aiir-sow-system-xxxxx.vercel.app/
```
**Expected:** `{"status":"healthy","service":"AIIR SOW Automation System"}`

**Test cron endpoint (manually trigger):**
```bash
curl https://aiir-sow-system-xxxxx.vercel.app/cron/watch-transcripts
```
**Expected:** `{"message":"Processed 0 files","total_files":0,...}`

**Check Vercel logs:**
- Dashboard → Functions → Logs
- Look for errors

**Time:** 5 minutes
**Complexity:** ⭐ (Very Easy)

---

### **Step 6: Upload Test Transcript** 📄

**Create test file:**
```
test-transcript.txt
---
Client Company: TechCorp
Decision Maker: kapurkartanmay@gmail.com
Decision Maker Name: Tanmay Kapur
Coachee Name: Jane Smith
Seniority: C-Suite
Duration: 16 weeks
Market Type: Hybrid

Transcript:
Jane is the Chief Marketing Officer at TechCorp. She's looking to improve her
self-awareness and executive presence. She mentioned wanting to understand how
others experience her leadership and develop her influence with stakeholders.

The budget for this engagement is approximately $25,000. She's interested in
starting within the next 2 weeks.
---
```

**Upload to Google Drive:**
1. Go to Transcripts folder: https://drive.google.com/drive/folders/1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu
2. Upload `test-transcript.txt`
3. Wait 5 minutes (cron runs every 5 min)
4. **OR** manually trigger:
   ```bash
   curl https://aiir-sow-system-xxxxx.vercel.app/cron/watch-transcripts
   ```

**Expected Results:**
1. Check Tracker Sheet - new row appears
2. Check your email (`kapurkartanmay@gmail.com`) - pricing review email
3. Click "Approve Pricing" button
4. Check email again - SOW review email
5. Click "Approve & Send to Client" button
6. Check Tracker - status = "completed"
7. Check Archive folder - transcript moved

**Time:** 5-10 minutes
**Complexity:** ⭐ (Very Easy)

---

## 📊 **Deployment Status Tracker**

- [ ] **Step 1:** Fix Gmail (Choose: Resend / OAuth2 / Domain Delegation)
- [ ] **Step 2:** Share Google resources with service account (7 items)
- [ ] **Step 3:** Deploy to Vercel
- [ ] **Step 4:** Configure environment variables (47 variables)
- [ ] **Step 5:** Test deployment (health check + cron)
- [ ] **Step 6:** Upload test transcript and verify workflow

**Estimated Total Time:** 1-2 hours (depending on email setup choice)

---

## 🚫 **Why You CAN'T Test Locally**

**Missing Components:**
1. ❌ **No Cron Job** - Needs Vercel scheduler (can't run every 5 min locally)
2. ❌ **No Public URLs** - Webhook buttons in emails need public internet access
3. ❌ **No 24/7 Server** - FastAPI needs to run continuously (Vercel handles this)

**What you CAN test locally:**
- ✅ Business logic: `python test_business_logic.py` (already working)
- ✅ Individual functions (if you write manual test scripts)

**What you CANNOT test locally:**
- ❌ Full end-to-end workflow
- ❌ Email sending
- ❌ Cron jobs
- ❌ Webhook approvals

---

## 🎯 **Recommended Next Steps**

### **For Quick Testing (Fastest):**
1. **Use Resend for emails** (10 min setup)
2. Share Google resources (10 min)
3. Deploy to Vercel (10 min)
4. Add environment variables (15 min)
5. Upload test transcript (5 min)

**Total:** ~1 hour to fully working system

### **For Production (Best):**
1. **Set up Gmail properly** (OAuth2 or domain delegation)
2. Share Google resources
3. Deploy to Vercel
4. Add environment variables
5. Test thoroughly

**Total:** ~2 hours to production-ready system

---

## ❓ **Which Email Option Should You Choose?**

**Answer these questions:**

1. Is `kapurkartanmay@gmail.com` a Google Workspace account (custom domain)?
   - **YES** → Use Domain-Wide Delegation (Option C)
   - **NO** → Continue to Q2

2. Do you want the simplest, most reliable solution?
   - **YES** → Use Resend (Option A) ⭐ **RECOMMENDED**
   - **NO** → Continue to Q3

3. Are you okay with token refresh every 7 days?
   - **YES** → Use Gmail OAuth2 (Option B)
   - **NO** → Go back and use Resend (Option A)

**My Recommendation:** **Use Resend** - it's the fastest, simplest, and most reliable option.

---

## 📞 **Need Help?**

**I can help you with:**
1. ✅ Converting the system to use Resend instead of Gmail
2. ✅ Setting up OAuth2 for Gmail
3. ✅ Creating base64 encoded credentials for Vercel
4. ✅ Writing deployment scripts
5. ✅ Creating local test scripts (limited functionality)

**Just let me know which email option you want to use!**

---

**Last Updated:** March 12, 2026
**Status:** Ready for deployment (pending email setup decision)
