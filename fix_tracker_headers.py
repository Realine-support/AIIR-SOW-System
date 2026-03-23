"""
Fix Tracker Sheet Headers
Clears old data and sets up clean headers for the simplified tracker
"""

from app.services.google_sheets import GoogleSheetsService
from app.config import get_config

def fix_tracker():
    config = get_config()
    sheets = GoogleSheetsService(config.google_credentials_path)

    # New simplified headers
    headers = [
        'Engagement ID',
        'Date',
        'Client',
        'Coachee',
        'Title',
        'Program',
        'Duration',
        'Total Price',
        'Payment Terms',
        'Calculator Link',
        'SOW Link',
        'Rationale',
        'Status',
        'Notes'
    ]

    print("Clearing old Tracker data...")
    # Clear all existing data
    sheets.service.spreadsheets().values().clear(
        spreadsheetId=config.tracker_sheet_id,
        range='Tracker!A1:Z1000'
    ).execute()

    print("Writing new headers...")
    # Write new headers
    sheets.service.spreadsheets().values().update(
        spreadsheetId=config.tracker_sheet_id,
        range='Tracker!A1:N1',
        valueInputOption='RAW',
        body={'values': [headers]}
    ).execute()

    # Get sheet metadata to find the Tracker sheet ID
    metadata = sheets.service.spreadsheets().get(spreadsheetId=config.tracker_sheet_id).execute()
    tracker_sheet_id = None
    for sheet in metadata.get('sheets', []):
        if sheet['properties']['title'] == 'Tracker':
            tracker_sheet_id = sheet['properties']['sheetId']
            break

    if tracker_sheet_id is not None:
        # Format header row (bold, background color)
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': tracker_sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 14
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'bold': True,
                            'fontSize': 11
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        }]

        sheets.service.spreadsheets().batchUpdate(
            spreadsheetId=config.tracker_sheet_id,
            body={'requests': requests}
        ).execute()

    print("✓ Tracker headers fixed!")
    print(f"View at: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")

if __name__ == '__main__':
    fix_tracker()
