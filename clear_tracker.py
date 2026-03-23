"""Clear Tracker data rows for fresh test"""
from app.services.google_sheets import GoogleSheetsService
from app.config import get_config

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)

# Clear all data rows (keep header row 1)
sheets.service.spreadsheets().values().clear(
    spreadsheetId=config.tracker_sheet_id,
    range='Tracker!A2:N1000'
).execute()

print('Tracker cleared - ready for fresh test')
