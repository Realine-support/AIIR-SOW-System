"""
Check what sheet tabs exist in the Tracking Sheet
"""

from app.services import GoogleSheetsService
from app.config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)

logger.info("Checking sheet tabs...")
logger.info(f"Spreadsheet ID: {config.tracker_sheet_id}")
logger.info(f"Expected tab name from config: '{config.tracker_tab_name}'")

service = sheets.service
spreadsheet = service.spreadsheets().get(
    spreadsheetId=config.tracker_sheet_id
).execute()

logger.info("\nAvailable sheet tabs:")
for sheet in spreadsheet['sheets']:
    title = sheet['properties']['title']
    sheet_id = sheet['properties']['sheetId']
    logger.info(f"  - '{title}' (ID: {sheet_id})")
