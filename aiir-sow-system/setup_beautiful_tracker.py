"""
Setup Beautiful Tracker Sheet
Creates a professionally designed tracker with colors, borders, and formatting
"""

from app.services.google_sheets import GoogleSheetsService
from app.config import get_config

def setup_beautiful_tracker():
    config = get_config()
    sheets = GoogleSheetsService(config.google_credentials_path)

    # Get the sheet metadata to find the sheet ID
    metadata = sheets.service.spreadsheets().get(spreadsheetId=config.tracker_sheet_id).execute()

    # Find the first sheet (should be the only one)
    first_sheet = metadata.get('sheets', [])[0]
    sheet_id = first_sheet['properties']['sheetId']
    sheet_title = first_sheet['properties']['title']

    print(f"Setting up Tracker on sheet: {sheet_title} (ID: {sheet_id})")

    # Define headers
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
        'Calculator',
        'SOW',
        'Status',
        'Notes'
    ]

    # Step 1: Rename the sheet to "Tracker"
    if sheet_title != 'Tracker':
        rename_request = {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'title': 'Tracker'
                },
                'fields': 'title'
            }
        }
        sheets.service.spreadsheets().batchUpdate(
            spreadsheetId=config.tracker_sheet_id,
            body={'requests': [rename_request]}
        ).execute()
        print("Sheet renamed to 'Tracker'")

    # Step 2: Write headers
    sheets.service.spreadsheets().values().update(
        spreadsheetId=config.tracker_sheet_id,
        range='Tracker!A1:M1',
        valueInputOption='RAW',
        body={'values': [headers]}
    ).execute()
    print("Headers written")

    # Step 3: Apply beautiful formatting
    requests = [
        # Freeze header row
        {
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'gridProperties': {
                        'frozenRowCount': 1
                    }
                },
                'fields': 'gridProperties.frozenRowCount'
            }
        },

        # Set column widths for better readability
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 1  # Engagement ID
                },
                'properties': {'pixelSize': 200},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 1,
                    'endIndex': 2  # Date
                },
                'properties': {'pixelSize': 100},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 2,
                    'endIndex': 4  # Client, Coachee
                },
                'properties': {'pixelSize': 150},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 4,
                    'endIndex': 6  # Title, Program
                },
                'properties': {'pixelSize': 120},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 6,
                    'endIndex': 8  # Duration, Total Price
                },
                'properties': {'pixelSize': 110},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 8,
                    'endIndex': 9  # Payment Terms
                },
                'properties': {'pixelSize': 180},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 9,
                    'endIndex': 11  # Calculator, SOW
                },
                'properties': {'pixelSize': 80},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 11,
                    'endIndex': 12  # Status
                },
                'properties': {'pixelSize': 130},
                'fields': 'pixelSize'
            }
        },
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 12,
                    'endIndex': 13  # Notes
                },
                'properties': {'pixelSize': 200},
                'fields': 'pixelSize'
            }
        },

        # Format header row - Dark blue background with white bold text
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 13
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.11, 'green': 0.23, 'blue': 0.45},  # Professional dark blue
                        'textFormat': {
                            'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                            'bold': True,
                            'fontSize': 11,
                            'fontFamily': 'Arial'
                        },
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE',
                        'borders': {
                            'top': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'bottom': {'style': 'SOLID', 'width': 2, 'color': {'red': 0, 'green': 0, 'blue': 0}},
                            'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}},
                            'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.8, 'green': 0.8, 'blue': 0.8}}
                        },
                        'padding': {
                            'top': 8,
                            'bottom': 8,
                            'left': 4,
                            'right': 4
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,borders,padding)'
            }
        },

        # Set header row height
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': 0,
                    'endIndex': 1
                },
                'properties': {'pixelSize': 40},
                'fields': 'pixelSize'
            }
        },

        # Format data rows (alternating colors for better readability)
        # Light gray for even rows
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,  # Apply to many rows
                    'startColumnIndex': 0,
                    'endColumnIndex': 13
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},  # White
                        'textFormat': {
                            'fontSize': 10,
                            'fontFamily': 'Arial'
                        },
                        'verticalAlignment': 'MIDDLE',
                        'borders': {
                            'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.9, 'green': 0.9, 'blue': 0.9}},
                            'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.95, 'green': 0.95, 'blue': 0.95}},
                            'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
                        },
                        'padding': {
                            'top': 6,
                            'bottom': 6,
                            'left': 4,
                            'right': 4
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,verticalAlignment,borders,padding)'
            }
        },

        # Add alternating row colors using banding
        {
            'addBanding': {
                'bandedRange': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,
                        'endRowIndex': 1000,
                        'startColumnIndex': 0,
                        'endColumnIndex': 13
                    },
                    'rowProperties': {
                        'headerColor': {'red': 0.11, 'green': 0.23, 'blue': 0.45},
                        'firstBandColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},  # White
                        'secondBandColor': {'red': 0.96, 'green': 0.97, 'blue': 0.98}  # Very light blue
                    }
                }
            }
        },

        # Center align specific columns
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 1,  # Date
                    'endColumnIndex': 2
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat.horizontalAlignment'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 5,  # Program
                    'endColumnIndex': 7  # Duration
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat.horizontalAlignment'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': 1000,
                    'startColumnIndex': 9,  # Calculator
                    'endColumnIndex': 12  # Status
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat.horizontalAlignment'
            }
        },
    ]

    # Execute all formatting requests
    sheets.service.spreadsheets().batchUpdate(
        spreadsheetId=config.tracker_sheet_id,
        body={'requests': requests}
    ).execute()

    print("Beautiful formatting applied!")
    print(f"\nTracker URL: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")

if __name__ == '__main__':
    setup_beautiful_tracker()
