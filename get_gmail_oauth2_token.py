"""
Gmail OAuth2 Token Generator

This script helps you get OAuth2 credentials for sending emails as aline@aiirconsulting.com
Run this once to get a refresh token, then add it to your .env file.

Prerequisites:
1. Go to Google Cloud Console: https://console.cloud.google.com
2. Select project: sales-ai-agent-484003
3. APIs & Services -> Credentials -> Create Credentials -> OAuth 2.0 Client ID
4. Application type: Desktop app
5. Name: "AIIR SOW System - Gmail OAuth"
6. Add authorized redirect URI: http://localhost:8080/
7. Download credentials JSON and save as: oauth_credentials.json (in this directory)

Note: This script uses a local web server for OAuth (port 8080).
Make sure the port is available when running this script.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_oauth2_token():
    """Run OAuth flow to get refresh token."""

    print("=" * 80)
    print("Gmail OAuth2 Token Generator")
    print("=" * 80)
    print()

    # Check if oauth_credentials.json exists
    if not os.path.exists('oauth_credentials.json'):
        print("ERROR: oauth_credentials.json not found!")
        print()
        print("Please follow these steps:")
        print()
        print("1. Go to: https://console.cloud.google.com")
        print("2. Select project: sales-ai-agent-484003")
        print("3. Click 'APIs & Services' -> 'Credentials'")
        print("4. Click '+ CREATE CREDENTIALS' -> 'OAuth client ID'")
        print("5. Application type: 'Desktop app'")
        print("6. Name: 'AIIR SOW System - Gmail OAuth'")
        print("7. Add authorized redirect URI: http://localhost:8080/")
        print("8. Click 'CREATE'")
        print("9. Click 'DOWNLOAD JSON'")
        print("10. Save as: oauth_credentials.json (in this directory)")
        print()
        print("Then run this script again.")
        print("=" * 80)
        return None

    print("Found oauth_credentials.json")
    print()
    print("Starting OAuth flow...")
    print("Your browser will open. Please:")
    print("1. Sign in as: aline@aiirconsulting.com")
    print("2. Click 'Allow' to grant permissions")
    print()

    try:
        # Run OAuth flow using local server (replaces deprecated OOB method)
        flow = InstalledAppFlow.from_client_secrets_file(
            'oauth_credentials.json',
            SCOPES
        )

        # Use run_local_server which automatically handles the redirect
        # This will open a browser and automatically capture the authorization code
        print("Opening browser for authorization...")
        print("If the browser doesn't open automatically, you'll see a URL to visit manually.")
        print()

        creds = flow.run_local_server(
            port=8080,  # Use port 8080 (or any available port)
            prompt='consent',
            success_message='Authorization successful! You can close this window and return to the terminal.',
            open_browser=True
        )

        print()
        print("=" * 80)
        print("SUCCESS! OAuth2 credentials obtained.")
        print("=" * 80)
        print()

        # Save credentials to file
        with open('gmail_token.json', 'w') as token_file:
            token_file.write(creds.to_json())

        print("Credentials saved to: gmail_token.json")
        print()

        # Extract values for .env
        token_data = json.loads(creds.to_json())

        print("=" * 80)
        print("ADD THESE TO YOUR .env FILE:")
        print("=" * 80)
        print()
        print("# Gmail OAuth2 Configuration")
        print("GMAIL_USE_OAUTH2=true")
        print(f"GMAIL_REFRESH_TOKEN={token_data['refresh_token']}")
        print(f"GMAIL_CLIENT_ID={token_data['client_id']}")
        print(f"GMAIL_CLIENT_SECRET={token_data['client_secret']}")
        print()
        print("=" * 80)
        print()

        # Also save to a text file for easy copying
        with open('gmail_oauth_env_vars.txt', 'w') as env_file:
            env_file.write("# Gmail OAuth2 Configuration\n")
            env_file.write("GMAIL_USE_OAUTH2=true\n")
            env_file.write(f"GMAIL_REFRESH_TOKEN={token_data['refresh_token']}\n")
            env_file.write(f"GMAIL_CLIENT_ID={token_data['client_id']}\n")
            env_file.write(f"GMAIL_CLIENT_SECRET={token_data['client_secret']}\n")

        print("Environment variables also saved to: gmail_oauth_env_vars.txt")
        print()
        print("NEXT STEPS:")
        print("1. Copy the 4 lines above to your .env file")
        print("2. Also add them to Vercel environment variables (when deploying)")
        print("3. The system will now use OAuth2 to send emails as aline@aiirconsulting.com")
        print()
        print("NOTE: Refresh token is valid for 7 days (or until password changes)")
        print("      If emails stop working, run this script again to get a new token.")
        print()
        print("=" * 80)

        return creds

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR during OAuth flow:")
        print(str(e))
        print("=" * 80)
        print()
        print("Common issues:")
        print("1. Browser didn't open? Copy the URL from above and open manually")
        print("2. 'redirect_uri_mismatch' error? Make sure you added http://localhost:8080/ as authorized redirect URI")
        print("3. Port 8080 already in use? Close other applications or change port in the script")
        print("4. Permission denied? Sign in as aline@aiirconsulting.com")
        print()
        return None

if __name__ == "__main__":
    get_oauth2_token()
