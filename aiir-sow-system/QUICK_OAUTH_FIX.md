# Quick Fix for OAuth Screen Issue

## What was the problem?
The OAuth script was using Google's deprecated `urn:ietf:wg:oauth:2.0:oob` redirect method, which was disabled by Google in October 2022.

## What changed?
✅ **Fixed**: Updated to use `run_local_server()` method which opens a browser and automatically captures the OAuth code

## To fix your OAuth and send emails:

### 1. Update OAuth Client Redirect URI (ONE TIME)
   - Go to: https://console.cloud.google.com
   - Select: **sales-ai-agent-484003**
   - Navigate: **APIs & Services** → **Credentials**
   - Click your Desktop app OAuth client
   - Add redirect URI: `http://localhost:8080/`
   - Click **SAVE**

### 2. Run the updated script:
   ```bash
   cd D:\AIIR\aiir-sow-system
   venv\Scripts\activate
   python get_gmail_oauth2_token.py
   ```

### 3. What will happen:
   - ✅ Browser opens automatically
   - ✅ Sign in with: **aline@aiirconsulting.com**
   - ✅ Click **Allow**
   - ✅ Browser shows success message
   - ✅ Terminal shows OAuth credentials

### 4. Copy the 4 lines to your `.env` file:
   ```env
   GMAIL_USE_OAUTH2=true
   GMAIL_REFRESH_TOKEN=...
   GMAIL_CLIENT_ID=...
   GMAIL_CLIENT_SECRET=...
   ```

### 5. Done!
Your email sending will now work.

---

## Still having issues?

See the full guide: [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)

Common fixes:
- **redirect_uri_mismatch** → Add `http://localhost:8080/` to authorized redirect URIs
- **Port in use** → Close apps using port 8080 or change port in script
- **Browser doesn't open** → Copy URL from terminal manually
