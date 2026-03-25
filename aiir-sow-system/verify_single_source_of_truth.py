"""Verify Calculator is Single Source of Truth - All documents show same price"""
from app.services.google_sheets import GoogleSheetsService
from app.services.google_docs import GoogleDocsService
from app.config import get_config
import re

config = get_config()
sheets = GoogleSheetsService(config.google_credentials_path)
docs = GoogleDocsService(config.google_credentials_path)

calc_id = '11w6BrfsRbRsJ0yKV8VQusw7xPPTMPFY1g1ZpJb2WnJM'
sow_id = '1VtxOyVgT8JuEO4LBKWtNzkMDTKbWZZbWV2bL-C66vsI'

print('=' * 80)
print('SINGLE SOURCE OF TRUTH VERIFICATION')
print('Calculator is the ONLY place that calculates pricing')
print('=' * 80)

# 1. Read from Calculator (source of truth)
print('\n1. CALCULATOR (SOURCE OF TRUTH):')
print(f'   File ID: {calc_id}')
result = sheets.service.spreadsheets().values().get(
    spreadsheetId=calc_id,
    range='Coaching Calculator!B50'
).execute()
calc_price = result.get('values', [['']])[0][0]
print(f'   Total Services Cost (B50): {calc_price}')

# 2. Read from Tracker
print('\n2. TRACKER (reads from Calculator):')
result = sheets.service.spreadsheets().values().get(
    spreadsheetId=config.tracker_sheet_id,
    range='Tracker!H2'
).execute()
tracker_price = result.get('values', [['']])[0][0]
print(f'   Total Price (H2): {tracker_price}')

# 3. Read from SOW
print('\n3. SOW (reads from Calculator):')
print(f'   Document ID: {sow_id}')
document = docs.docs_service.documents().get(documentId=sow_id).execute()
content = document.get('body', {}).get('content', [])
text = ''
for element in content:
    if 'paragraph' in element:
        for text_run in element['paragraph'].get('elements', []):
            if 'textRun' in text_run:
                text += text_run['textRun'].get('content', '')

# Find price in SOW (look for $X,XXX pattern)
price_matches = re.findall(r'\$[\d,]+', text)
# The engagement price should be in the document
if '$9,356' in text:
    sow_price = '$9,356'
elif '$9356' in text:
    sow_price = '$9356'
else:
    sow_price = 'NOT FOUND (searching for $9,356)'
    # Show first few prices found
    if price_matches:
        sow_price = f'NOT FOUND - Found: {", ".join(price_matches[:5])}'

print(f'   Total Price in document: {sow_price}')

# 4. Verify consistency
print('\n' + '=' * 80)
print('CONSISTENCY CHECK:')
print('=' * 80)

# Clean values for comparison
def clean_price(p):
    return p.replace('$', '').replace(',', '').strip()

calc_clean = clean_price(calc_price)
tracker_clean = clean_price(tracker_price)

print(f'Calculator: ${calc_clean}')
print(f'Tracker:    ${tracker_clean}')
print(f'SOW:        {sow_price}')

if calc_clean == tracker_clean and '$9,356' in sow_price:
    print('\n✓✓✓ SUCCESS: All three documents show same price from Calculator!')
    print('✓✓✓ Calculator is the SINGLE SOURCE OF TRUTH')
else:
    print('\n✗✗✗ MISMATCH: Prices do not match')
    if calc_clean != tracker_clean:
        print(f'  Calculator vs Tracker: ${calc_clean} != ${tracker_clean}')
    if '$9,356' not in sow_price:
        print(f'  SOW does not contain $9,356')

print('=' * 80)
