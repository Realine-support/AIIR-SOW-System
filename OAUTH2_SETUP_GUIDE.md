# Gmail OAuth2 Setup Guide for AIIR SOW System

**Date:** March 12, 2026
**Purpose:** Set up OAuth2 authentication so the system can send emails as `aline@aiirconsulting.com`

---

## 📋 **Overview**

Since you don't have Google Workspace admin access for domain-wide delegation, we'll use OAuth2 user authentication instead. This allows the system to send emails as `aline@aiirconsulting.com` after you authorize it once.

**Pros:**
- ✅ No admin access needed
- ✅ Works with any Google account
- ✅ Set up in 20-30 minutes

**Cons:**
- ⚠️ Refresh token expires every 7 days (or when password changes)
- ⚠️ Need to re-authorize when token expires

---

## 🚀 **Step-by-Step Setup**

### **Step 1: Create OAuth 2.0 Credentials in Google Cloud Console**

**1.1** Go to Google Cloud Console:
```
https://console.cloud.google.com/apis/credentials?project=sales-ai-agent-484003
```

**1.2** Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

**1.3** If prompted to configure OAuth consent screen:
   - Click **"CONFIGURE CONSENT SCREEN"**
   - User Type: **Internal** (if using Google Workspace) OR **External** (if personal Gmail)
   - Click **"CREATE"**

**1.4** Fill in OAuth consent screen (minimum fields):
   - App name: `AIIR SOW Automation`
   - User support email: `aline@aiirconsulting.com`
   - Developer contact: `aline@aiirconsulting.com`
   - Click **"SAVE AND CONTINUE"**

**1.5** Scopes screen:
   - Click **"ADD OR REMOVE SCOPES"**
   - Search for: `gmail.send`
   - Check: `https://www.googleapis.com/auth/gmail.send`
   - Also add (already in project):
     - `https://www.googleapis.com/auth/drive`
     - `https://www.googleapis.com/auth/documents`
     - `https://www.googleapis.com/auth/spreadsheets`
   - Click **"UPDATE"** → **"SAVE AND CONTINUE"**

**1.6** Test users (if External):
   - Click **"+ ADD USERS"**
   - Add: `aline@aiirconsulting.com`
   - Click **"SAVE AND CONTINUE"**

**1.7** Summary:
   - Click **"BACK TO DASHBOARD"**

**1.8** Now create the OAuth client:
   - Go back to: https://console.cloud.google.com/apis/credentials?project=sales-ai-agent-484003
   - Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
   - Application type: **Desktop app**
   - Name: `AIIR SOW System - Gmail OAuth`
   - Click **"CREATE"**

**1.9** Download credentials:
   - Click **"DOWNLOAD JSON"**
   - Save file as: `oauth_credentials.json` in `d:\AIIR\aiir-sow-system\`

---

### **Step 2: Run OAuth Flow to Get Refresh Token**

**2.1** Open terminal/command prompt:
```bash
cd d:\AIIR\aiir-sow-system
```

**2.2** Activate virtual environment:
```bash
venv\Scripts\activate
```

**2.3** Run the OAuth token script:
```bash
python get_gmail_oauth2_token.py
```

**2.4** What happens:
- Browser window will open automatically
- **IMPORTANT:** Sign in as `aline@aiirconsulting.com` (NOT your personal email!)
- You'll see a warning: "Google hasn't verified this app"
  - Click **"Advanced"**
  - Click **"Go to AIIR SOW Automation (unsafe)"** ← This is safe, it's your own app
- Review permissions:
  - "Send email on your behalf"
  - "See, edit, create, and delete all of your Google Drive files"
  - etc.
- Click **"Allow"**

**2.5** After allowing, you'll see:
```
================================================================================
SUCCESS! OAuth2 credentials obtained.
================================================================================

ADD THESE TO YOUR .env FILE:
================================================================================

# Gmail OAuth2 Configuration
GMAIL_USE_OAUTH2=true
GMAIL_REFRESH_TOKEN=1//0xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_CLIENT_ID=xxxxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxx

================================================================================
```

**2.6** Copy these 4 lines!

---

### **Step 3: Add OAuth Credentials to .env File**

**3.1** Open `.env` file:
```bash
cd d:\AIIR\aiir-sow-system
notepad .env
```

**3.2** Add the 4 lines from Step 2.5:
```bash
# Gmail OAuth2 Configuration
GMAIL_USE_OAUTH2=true
GMAIL_REFRESH_TOKEN=1//0xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_CLIENT_ID=xxxxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxx
```

**3.3** Verify existing email config is still there:
```bash
GMAIL_SEND_AS=aline@aiirconsulting.com
REVIEW_EMAIL_TO=kapurkartanmay@gmail.com
CLIENT_EMAIL_FROM=aline@aiirconsulting.com
```

**3.4** Save and close `.env`

---

### **Step 4: Test OAuth2 Locally (Optional)**

**4.1** Create a test script:
```bash
cd d:\AIIR\aiir-sow-system
notepad test_oauth_email.py
```

**4.2** Paste this code:
```python
from app.config import get_config
from app.services.gmail_service import GmailService

config = get_config()

# Initialize Gmail with OAuth2
gmail = GmailService(
    config.google_credentials_path,
    config.gmail_send_as,
    use_oauth2=config.gmail_use_oauth2,
    oauth2_refresh_token=config.gmail_refresh_token,
    oauth2_client_id=config.gmail_client_id,
    oauth2_client_secret=config.gmail_client_secret
)

# Send test email
print("Sending test email...")
message_id = gmail.send_email(
    to="kapurkartanmay@gmail.com",
    subject="Test Email from AIIR SOW System (OAuth2)",
    body="<h1>Success!</h1><p>OAuth2 is working correctly.</p>",
    is_html=True
)

print(f"Email sent! Message ID: {message_id}")
print("Check kapurkartanmay@gmail.com for the test email.")
```

**4.3** Run the test:
```bash
venv\Scripts\python test_oauth_email.py
```

**4.4** Check `kapurkartanmay@gmail.com` for test email from `aline@aiirconsulting.com`

**If you get an error:**
- Check that all 4 OAuth variables are in `.env`
- Check that `GMAIL_USE_OAUTH2=true` (not `false`)
- Make sure you signed in as `aline@aiirconsulting.com` during OAuth flow

---

### **Step 5: Deploy to Vercel with OAuth2**

**Now that OAuth2 works locally, deploy to Vercel!**

Follow the main deployment guide: `DEPLOYMENT_GUIDE_YOUR_SETUP.md`

**IMPORTANT:** When adding environment variables to Vercel, include these OAuth2 variables:

```bash
GMAIL_USE_OAUTH2=true
GMAIL_REFRESH_TOKEN=1//0xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_CLIENT_ID=xxxxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxx
```

---

## 🔄 **Token Refresh (When Emails Stop Working)**

**OAuth2 refresh tokens expire after ~7 days or when:**
- `aline@aiirconsulting.com` password is changed
- OAuth consent is revoked
- Token is invalidated

**Symptoms:**
- Emails stop sending
- Vercel logs show: `401 Unauthorized` or `invalid_grant`

**Solution:**
1. Run OAuth flow again:
   ```bash
   cd d:\AIIR\aiir-sow-system
   venv\Scripts\python get_gmail_oauth2_token.py
   ```
2. Sign in as `aline@aiirconsulting.com`
3. Get new `GMAIL_REFRESH_TOKEN`
4. Update in Vercel:
   - Dashboard → Project → Settings → Environment Variables
   - Find `GMAIL_REFRESH_TOKEN`
   - Click "Edit"
   - Paste new token
   - Save
5. Redeploy (or wait for next cron run)

---

## 📊 **Comparison: OAuth2 vs Domain-Wide Delegation**

| Feature | OAuth2 (Your Setup) | Domain-Wide Delegation |
|---------|---------------------|------------------------|
| Admin Access Needed | ❌ No | ✅ Yes |
| Setup Time | 20-30 min | 5-10 min |
| Token Expiration | 7 days | Never |
| Manual Refresh | ✅ Yes (re-run script) | ❌ No |
| Works For | Any Google account | Google Workspace only |
| Best For | Testing, small teams | Production, enterprises |

---

## 🔒 **Security Notes**

**1. Keep credentials safe:**
- ✅ `oauth_credentials.json` is in `.gitignore`
- ✅ `.env` is in `.gitignore`
- ✅ Never commit OAuth tokens to git

**2. Refresh token storage:**
- ⚠️ Refresh token gives full access to `aline@aiirconsulting.com`'s Gmail
- ⚠️ Store securely in Vercel environment variables (encrypted)
- ⚠️ Don't share or expose publicly

**3. Revoking access:**
If you need to revoke access:
- Go to: https://myaccount.google.com/permissions
- Sign in as `aline@aiirconsulting.com`
- Find "AIIR SOW Automation"
- Click "Remove access"

---

## ❓ **Troubleshooting**

### **Issue 1: Browser doesn't open**

**Error:** `Please visit this URL to authorize...`

**Solution:**
- Copy the URL from terminal
- Paste in browser manually
- Continue with OAuth flow

---

### **Issue 2: "redirect_uri_mismatch" error**

**Cause:** Created "Web application" instead of "Desktop app"

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials?project=sales-ai-agent-484003
2. Find your OAuth client
3. Click "Delete"
4. Create new one as **"Desktop app"** (Step 1.8)
5. Download new `oauth_credentials.json`
6. Run script again

---

### **Issue 3: "Access blocked: This app's request is invalid"**

**Cause:** Missing OAuth consent screen configuration

**Solution:**
- Follow Step 1.3 - 1.7 carefully
- Make sure you added all required scopes
- Add `aline@aiirconsulting.com` as test user (if External)

---

### **Issue 4: Emails not sending after deployment**

**Check:**
1. All 4 OAuth variables in Vercel environment variables?
2. `GMAIL_USE_OAUTH2=true` (not `false`)?
3. Token expired? (re-run OAuth script)
4. Check Vercel logs for specific error

---

## 📝 **Files Created**

After completing this setup, you'll have:

```
d:\AIIR\aiir-sow-system\
├── oauth_credentials.json        # OAuth client credentials (DON'T COMMIT)
├── gmail_token.json              # Generated token (DON'T COMMIT)
├── gmail_oauth_env_vars.txt      # Copy of env vars (DON'T COMMIT)
├── get_gmail_oauth2_token.py     # Token generation script
├── test_oauth_email.py           # Test script (optional)
└── .env                          # Updated with OAuth vars (DON'T COMMIT)
```

**All sensitive files are already in `.gitignore` ✅**

---

## ✅ **Success Checklist**

- [ ] Created OAuth 2.0 client in Google Cloud Console
- [ ] Downloaded `oauth_credentials.json`
- [ ] Ran `get_gmail_oauth2_token.py`
- [ ] Signed in as `aline@aiirconsulting.com`
- [ ] Granted permissions
- [ ] Copied 4 OAuth variables to `.env`
- [ ] Tested sending email locally (optional)
- [ ] Added OAuth variables to Vercel environment variables
- [ ] System sending emails successfully!

---

## 🎯 **Next Steps**

Once OAuth2 is working:

1. **Share Google Resources** (if not done yet)
   - Share Tracker Sheet, folders with service account
   - See: `DEPLOYMENT_GUIDE_YOUR_SETUP.md` Step 1

2. **Deploy to Vercel**
   - Follow: `DEPLOYMENT_GUIDE_YOUR_SETUP.md` Steps 2-10

3. **Test Full Workflow**
   - Upload test transcript
   - Verify emails are sent
   - Check complete workflow

---

**Questions?** Check `DEPLOYMENT_GUIDE_YOUR_SETUP.md` for complete deployment instructions!

**Last Updated:** March 12, 2026
**Status:** OAuth2 setup ready to use ✅
