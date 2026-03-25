"""
Verification script for the workflow fix
Checks that the engagement was created correctly in the tracking sheet
"""

from app.services import GoogleSheetsService
from app.config import get_config

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)

print("Verifying tracking sheet contents...")
print("="*70)

values = sheets.read_range(config.tracker_sheet_id, "Tracker!A:M")
print(f"\nTotal rows: {len(values)}\n")

for idx, row in enumerate(values, start=1):
    if row and len(row) > 0:
        eng_id = row[0] if len(row) > 0 else ''
        client = row[2] if len(row) > 2 else ''
        program = row[5] if len(row) > 5 else ''
        sow_col = row[10] if len(row) > 10 else ''
        status = row[11] if len(row) > 11 else ''

        sow_status = "EMPTY (correct)" if not sow_col else f"HAS_URL (WRONG!): {sow_col[:30]}"

        print(f"Row {idx}:")
        print(f"  Engagement ID: {eng_id}")
        print(f"  Client: {client}")
        print(f"  Program: {program}")
        print(f"  Column K (SOW): {sow_status}")
        print(f"  Status: {status}")
        print()

# Check latest engagement
print("\n" + "="*70)
print("Checking latest engagement (row 4)...")
if len(values) >= 4:
    row_4 = values[3]  # 0-indexed
    if row_4:
        engagement_id = row_4[0] if len(row_4) > 0 else ''
        sow_url = row_4[10] if len(row_4) > 10 else ''

        if engagement_id.startswith('GLOBALTECH-20260325-01'):
            print(f"Found latest engagement: {engagement_id}")
            if not sow_url:
                print("Column K (SOW) is EMPTY - CORRECT!")
            else:
                print(f"Column K (SOW) has URL - WRONG: {sow_url}")
        else:
            print(f"Unexpected engagement ID in row 4: {engagement_id}")
else:
    print("Row 4 does not exist yet")

print("\nVerification complete!")
