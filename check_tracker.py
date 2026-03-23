"""Check Tracker row"""
from app.services.google_sheets import GoogleSheetsService
from app.config import get_config

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)

result = sheets.service.spreadsheets().values().get(
    spreadsheetId=config.tracker_sheet_id,
    range='Tracker!A2:M2'
).execute()

data = result.get('values', [[]])[0] if result.get('values') else []

headers = [
    'Engagement ID', 'Date', 'Client', 'Coachee', 'Title',
    'Program', 'Duration', 'Total Price', 'Payment Terms',
    'Calculator', 'SOW', 'Rationale', 'Status'
]

print('TRACKER ROW:')
for i in range(min(len(headers), len(data))):
    print(f'  {headers[i]}: {data[i]}')
