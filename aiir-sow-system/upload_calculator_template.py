"""
Upload Excel Calculator Template to Google Drive and convert to Google Sheets
This creates the master template that will be duplicated for each client
"""

import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from app.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_calculator_template():
    """Upload Excel template to Drive and convert to Google Sheets"""

    config = get_config()

    # Build Drive service
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        config.google_credentials_path,
        scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=credentials)

    # Excel file path
    excel_path = 'D:/AIIR/MASTER of Bespoke_Integrated Solutions_Costing_Calculator_v1.xlsx'

    logger.info(f"Uploading Excel template: {excel_path}")
    logger.info(f"Converting to Google Sheets format...")

    # Upload and convert to Google Sheets
    file_metadata = {
        'name': 'MASTER_Calculator_Template',
        'parents': [config.sow_templates_folder_id],  # Put in SOW Templates folder
        'mimeType': 'application/vnd.google-apps.spreadsheet'  # Convert to Google Sheets
    }

    media = MediaFileUpload(
        excel_path,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        resumable=True
    )

    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, name'
    ).execute()

    file_id = file.get('id')
    web_link = file.get('webViewLink')
    name = file.get('name')

    logger.info("=" * 80)
    logger.info("✓ UPLOAD SUCCESSFUL!")
    logger.info("=" * 80)
    logger.info(f"File Name: {name}")
    logger.info(f"File ID: {file_id}")
    logger.info(f"URL: {web_link}")
    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info(f"1. Add this to your .env file:")
    logger.info(f"   CALCULATOR_TEMPLATE_ID={file_id}")
    logger.info("")
    logger.info("2. Open the template and verify formatting looks good:")
    logger.info(f"   {web_link}")
    logger.info("")
    logger.info("3. Note which cells should be populated with data")
    logger.info("=" * 80)

    return file_id, web_link


if __name__ == "__main__":
    upload_calculator_template()
