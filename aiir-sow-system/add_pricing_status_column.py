"""
Script to add "Pricing Model Status" column (Column U) to Tracking Sheet
This adds the header and sets up data validation dropdown
"""

from app.services import GoogleSheetsService
from app.config import get_config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_pricing_status_column():
    """Add Pricing Model Status column to Tracking Sheet"""

    config = get_config()
    sheets = GoogleSheetsService(config.google_credentials_path)

    logger.info("=" * 80)
    logger.info("Adding 'Pricing Model Status' column to Tracking Sheet")
    logger.info("=" * 80)

    # Step 1: Read current headers
    logger.info("Step 1: Reading current headers from Tracker sheet")
    headers_range = f"{config.tracker_tab_name}!A1:Z1"
    headers = sheets.read_range(config.tracker_sheet_id, headers_range)

    if headers:
        current_headers = headers[0]
        logger.info(f"Current columns: {len(current_headers)}")
        logger.info(f"Last column: {current_headers[-1] if current_headers else 'None'}")
    else:
        logger.error("No headers found!")
        return

    # Step 2: Check if Column U already exists
    if len(current_headers) >= 21:  # Column U is the 21st column
        if current_headers[20] == "Pricing Model Status":
            logger.info("✓ Column U 'Pricing Model Status' already exists!")
            logger.info("Will verify/update data validation and formatting...")
        else:
            logger.warning(f"Column U exists but has different name: '{current_headers[20]}'")
            logger.info("Will update Column U header...")

    # Step 3: Add/Update Column U header
    logger.info("Step 2: Adding 'Pricing Model Status' header to Column U")
    sheets.update_range(
        config.tracker_sheet_id,
        f"{config.tracker_tab_name}!U1",
        [["Pricing Model Status"]]
    )
    logger.info("✓ Added header to Column U")

    # Step 4: Add data validation using Google Sheets API directly
    logger.info("Step 3: Adding dropdown data validation to Column U")

    # Get the sheet ID (not the spreadsheet ID)
    service = sheets.service
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=config.tracker_sheet_id
    ).execute()

    # Find the Tracker tab
    sheet_id = None
    logger.info(f"Looking for sheet tab named: '{config.tracker_tab_name}'")
    logger.info(f"Available sheets:")
    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        sid = sheet['properties']['sheetId']
        logger.info(f"  - '{title}' (ID: {sid})")
        if title == config.tracker_tab_name:
            sheet_id = sid
            break

    if sheet_id is None:
        logger.error(f"Could not find sheet ID for '{config.tracker_tab_name}'")
        logger.error("Available sheets listed above")
        return

    logger.info(f"Found sheet ID: {sheet_id}")

    # Create data validation request
    # Column U is column index 20 (0-indexed)
    requests = [{
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,  # Start from row 2 (after header)
                "startColumnIndex": 20,  # Column U (0-indexed)
                "endColumnIndex": 21  # Column U only
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [
                        {"userEnteredValue": "Pending Review"},
                        {"userEnteredValue": "Approved"},
                        {"userEnteredValue": "Disapproved"}
                    ]
                },
                "showCustomUi": True,
                "strict": False
            }
        }
    }]

    # Execute the request
    body = {"requests": requests}
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.tracker_sheet_id,
        body=body
    ).execute()

    logger.info("✓ Added dropdown validation to Column U")
    logger.info("  Options: Pending Review, Approved, Disapproved")

    # Step 5: Add conditional formatting (optional - for visual clarity)
    logger.info("Step 4: Adding conditional formatting to Column U")

    format_requests = [
        # Green for "Approved"
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 20,
                        "endColumnIndex": 21
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Approved"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 0.8, "green": 1.0, "blue": 0.8}
                        }
                    }
                },
                "index": 0
            }
        },
        # Yellow for "Pending Review"
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 20,
                        "endColumnIndex": 21
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Pending Review"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.8}
                        }
                    }
                },
                "index": 0
            }
        },
        # Red for "Disapproved"
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "startColumnIndex": 20,
                        "endColumnIndex": 21
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": "Disapproved"}]
                        },
                        "format": {
                            "backgroundColor": {"red": 1.0, "green": 0.8, "blue": 0.8}
                        }
                    }
                },
                "index": 0
            }
        }
    ]

    body = {"requests": format_requests}
    service.spreadsheets().batchUpdate(
        spreadsheetId=config.tracker_sheet_id,
        body=body
    ).execute()

    logger.info("✓ Added conditional formatting:")
    logger.info("  - Green background for 'Approved'")
    logger.info("  - Yellow background for 'Pending Review'")
    logger.info("  - Red background for 'Disapproved'")

    logger.info("=" * 80)
    logger.info("✓✓✓ TRACKING SHEET UPDATED SUCCESSFULLY ✓✓✓")
    logger.info("")
    logger.info("Column U 'Pricing Model Status' has been added with:")
    logger.info("  1. Header in row 1")
    logger.info("  2. Dropdown validation (Pending Review, Approved, Disapproved)")
    logger.info("  3. Conditional formatting (colors)")
    logger.info("")
    logger.info("You can now:")
    logger.info("  - Run the workflows to test Part 1 (pricing model generation)")
    logger.info("  - Change Column U to 'Approved' to trigger Part 2 (SOW generation)")
    logger.info("")
    logger.info(f"View sheet: https://docs.google.com/spreadsheets/d/{config.tracker_sheet_id}")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        add_pricing_status_column()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
