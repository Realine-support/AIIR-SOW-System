# Gmail OAuth Setup Guide

## Problem Fixed
The OAuth flow was using the deprecated `urn:ietf:wg:oauth:2.0:oob` method which Google disabled in October 2022. The script has been updated to use a local web server for OAuth authentication.

---

## One-Time Setup Steps

### Step 1: Configure Google Cloud Console OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: **sales-ai-agent-484003**
3. Navigate to **APIs & Services** → **Credentials**
4. If you already have an OAuth 2.0 Client ID:
   - Click on the existing Desktop app client
   - Under **Authorized redirect URIs**, add: `http://localhost:8080/`
   - Click **SAVE**

5. If you need to create a new OAuth 2.0 Client ID:
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Application type: **Desktop app**
   - Name: **AIIR SOW System - Gmail OAuth**
   - Click **ADD URI** under Authorized redirect URIs
   - Add: `http://localhost:8080/`
   - Click **CREATE**

6. Download the credentials JSON file:
   - Click the download icon (⬇) next to your OAuth 2.0 Client ID
   - Save the file as `oauth_credentials.json` in the `aiir-sow-system` directory

---

### Step 2: Run the OAuth Token Generator

1. Open a terminal/command prompt
2. Navigate to the project directory:
   ```bash
   cd D:\AIIR\aiir-sow-system
   ```

3. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

4. Run the OAuth script:
   ```bash
   python get_gmail_oauth2_token.py
   ```

5. The script will:
   - Open your default web browser automatically
   - Navigate to the Google OAuth consent screen
   - **IMPORTANT**: Sign in with **aline@aiirconsulting.com** (or the email you want to send from)
   - Click **Allow** to grant Gmail send permissions
   - Automatically redirect back to the script
   - Display success message in the browser

6. The script will save:
   - `gmail_token.json` - Contains the OAuth credentials
   - `gmail_oauth_env_vars.txt` - Contains the environment variables to add to `.env`

---

### Step 3: Update Your .env File

Copy the 4 lines from the terminal output (or from `gmail_oauth_env_vars.txt`) and add them to your `.env` file:

```env
# Gmail OAuth2 Configuration
GMAIL_USE_OAUTH2=true
GMAIL_REFRESH_TOKEN=<your_refresh_token>
GMAIL_CLIENT_ID=<your_client_id>
GMAIL_CLIENT_SECRET=<your_client_secret>
```

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution**: Make sure you added `http://localhost:8080/` as an authorized redirect URI in Google Cloud Console (Step 1).

### Error: "Port 8080 already in use"
**Solutions**:
1. Close any applications using port 8080, OR
2. Edit `get_gmail_oauth2_token.py` and change the port number on line 75:
   ```python
   creds = flow.run_local_server(
       port=8081,  # Change to any available port
       ...
   )
   ```
   Then update the redirect URI in Google Cloud Console to match (e.g., `http://localhost:8081/`)

### Browser doesn't open automatically
**Solution**: The script will print the authorization URL. Copy and paste it into your browser manually.

### Error: "Permission denied"
**Solution**: Make sure you're signing in with the correct Google account (aline@aiirconsulting.com).

### Refresh token expires
**Note**: Refresh tokens can expire after:
- 7 days of inactivity (for test/unverified apps)
- Password change
- User revokes access

If emails stop working, simply run the OAuth script again to get a new refresh token.

---

## How It Works

1. **OAuth 2.0 Flow**: The script uses Google's OAuth 2.0 protocol to get user consent
2. **Local Server**: A temporary web server runs on `localhost:8080` to receive the OAuth callback
3. **Refresh Token**: After authorization, you get a refresh token that can be used to get new access tokens
4. **Gmail Service**: The application uses the refresh token to send emails on behalf of the authorized account

---

## Security Notes

- **Keep secrets safe**: Never commit `oauth_credentials.json`, `gmail_token.json`, or `.env` to version control
- **Refresh token**: Treat refresh tokens like passwords - they provide access to send emails
- **Scope**: The OAuth token only has permission to send emails (`gmail.send` scope)

---

## Deployment (Vercel)

When deploying to Vercel or other platforms:

1. Add these environment variables to your deployment platform:
   ```
   GMAIL_USE_OAUTH2=true
   GMAIL_REFRESH_TOKEN=<your_refresh_token>
   GMAIL_CLIENT_ID=<your_client_id>
   GMAIL_CLIENT_SECRET=<your_client_secret>
   ```

2. The refresh token is the same one generated locally - you only need to run the OAuth flow once

3. Make sure your Google Cloud Console OAuth app is configured for production use if you're sending many emails

---

## Alternative: Service Account (Advanced)

If OAuth becomes too cumbersome, you can use a Service Account with domain-wide delegation:

1. Requires Google Workspace admin access
2. No refresh token needed
3. More complex setup
4. Better for production use

Contact your Google Workspace admin if you want to set this up instead.
