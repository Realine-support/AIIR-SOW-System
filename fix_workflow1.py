import json, copy

with open('D:/AIIR/n8n/workflow_1_transcript_pricing.json', 'r', encoding='utf-8') as f:
    w = json.load(f)

SHEET_CRED = {"id": "pQl0UnpSh855m4lW", "name": "Tanmay"}
SHEET_ID   = "1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA"

# ── 1. Update Google Sheets credential on all nodes ───────────────────────────
for node in w['nodes']:
    if 'googleSheetsOAuth2Api' in node.get('credentials', {}):
        node['credentials']['googleSheetsOAuth2Api'] = SHEET_CRED

# ── 2. Replace sheet ID variable with actual ID in HTTP request URLs ──────────
for node in w['nodes']:
    url = node.get('parameters', {}).get('url', '')
    if '{{$vars.AIIR_PRICING_SHEET_ID}}' in url:
        node['parameters']['url'] = url.replace(
            '{{$vars.AIIR_PRICING_SHEET_ID}}', SHEET_ID
        )

# ── 3. Fix Write to Tracker Sheet — add schema + full value mapping ───────────
tracker_schema = [
    {"id": "engagement_id",           "displayName": "engagement_id",           "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "created_at",              "displayName": "created_at",              "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "transcript_filename",     "displayName": "transcript_filename",     "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "client_company",          "displayName": "client_company",          "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "coachee_name",            "displayName": "coachee_name",            "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "hubspot_deal_id",         "displayName": "hubspot_deal_id",         "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "coach_name",              "displayName": "coach_name",              "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "tier",                    "displayName": "tier",                    "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "bill_rate",               "displayName": "bill_rate",               "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "num_participants",        "displayName": "num_participants",        "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "price_per_participant",   "displayName": "price_per_participant",   "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "total_engagement_price",  "displayName": "total_engagement_price",  "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "payment_structure",       "displayName": "payment_structure",       "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "net_days",                "displayName": "net_days",                "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "pricing_approval_status", "displayName": "pricing_approval_status", "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "pricing_approved_by",     "displayName": "pricing_approved_by",     "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "pricing_approved_at",     "displayName": "pricing_approved_at",     "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "rationale_doc_url",       "displayName": "rationale_doc_url",       "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "calculator_url",          "displayName": "calculator_url",          "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "sow_doc_url",             "displayName": "sow_doc_url",             "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "sow_approval_status",     "displayName": "sow_approval_status",     "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "sow_approved_by",         "displayName": "sow_approved_by",         "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "sow_approved_at",         "displayName": "sow_approved_at",         "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "client_email",            "displayName": "client_email",            "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "sent_at",                 "displayName": "sent_at",                 "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "archive_folder_url",      "displayName": "archive_folder_url",      "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
    {"id": "full_variables_json",     "displayName": "full_variables_json",     "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
]

for node in w['nodes']:
    if node['name'] == 'Write to Tracker Sheet':
        node['parameters']['documentId'] = {"__rl": True, "value": SHEET_ID, "mode": "id"}
        node['parameters']['columns'] = {
            "mappingMode": "defineBelow",
            "value": {
                "engagement_id":          "={{ $json.engagementId }}",
                "created_at":             "={{ $json.createdAt }}",
                "transcript_filename":    "={{ $json.filename }}",
                "client_company":         "={{ $json.client_company }}",
                "coachee_name":           "={{ $json.coachee_name }}",
                "hubspot_deal_id":        "={{ $json.hubspot_deal_id }}",
                "coach_name":             "={{ $json.coachName }}",
                "tier":                   "={{ $json.tier }}",
                "bill_rate":              "={{ $json.billRate }}",
                "num_participants":       "={{ $json.num_participants }}",
                "payment_structure":      "={{ $json.paymentStructure }}",
                "net_days":               "={{ $json.netDays }}",
                "pricing_approval_status":"PENDING",
                "client_email":           "={{ $json.client_email }}",
                "full_variables_json":    "={{ JSON.stringify($json) }}"
            },
            "matchingColumns": [],
            "schema": tracker_schema,
            "attemptToConvertTypes": False,
            "convertFieldsToString": False
        }

# ── 4. Fix Write Calculator Cells — hardcode sheet ID and add correct body ────
for node in w['nodes']:
    if node['name'] == 'Write Calculator Cells':
        node['parameters']['url'] = f"=https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values:batchUpdate"
        node['parameters']['sendBody'] = True
        node['parameters']['contentType'] = "json"
        node['parameters']['body'] = (
            '={\n'
            '  "valueInputOption": "USER_ENTERED",\n'
            '  "data": [\n'
            '    { "range": "Calculator!H49", "values": [[{{ $json.num_participants }}]] },\n'
            '    { "range": "Calculator!B2",  "values": [["{{ $json.tier }}"]] },\n'
            '    { "range": "Calculator!B15", "values": [[{{ $json.billRate }}]] },\n'
            '    { "range": "Calculator!B16", "values": [[0.65]] },\n'
            '    { "range": "Calculator!B37", "values": [[{{ $json.hours.B37 }}]] },\n'
            '    { "range": "Calculator!B38", "values": [[{{ $json.hours.B38 }}]] },\n'
            '    { "range": "Calculator!B39", "values": [[{{ $json.hours.B39 }}]] },\n'
            '    { "range": "Calculator!B40", "values": [[{{ $json.hours.B40 }}]] },\n'
            '    { "range": "Calculator!B41", "values": [[{{ $json.hours.B41 }}]] },\n'
            '    { "range": "Calculator!B42", "values": [[{{ $json.hours.B42 }}]] },\n'
            '    { "range": "Calculator!B43", "values": [[{{ $json.hours.B43 }}]] },\n'
            '    { "range": "Calculator!B44", "values": [[{{ $json.hours.B44 }}]] },\n'
            '    { "range": "Calculator!B45", "values": [[{{ $json.hours.B45 }}]] },\n'
            '    { "range": "Calculator!B46", "values": [[{{ $json.hours.B46 }}]] },\n'
            '    { "range": "Calculator!E37", "values": [[{{ $json.hours.E37_CZ }}]] },\n'
            '    { "range": "Calculator!F38", "values": [[{{ $json.czRate }}]] },\n'
            '    { "range": "Calculator!H45", "values": [[{{ $json.fixedAssessmentFees }}]] }\n'
            '  ]\n'
            '}'
        )
        # Remove old bodyParameters if present
        node['parameters'].pop('bodyParameters', None)

# ── 5. Fix Read Calculated Price — hardcode sheet ID ─────────────────────────
for node in w['nodes']:
    if node['name'] == 'Read Calculated Price':
        node['parameters']['url'] = f"=https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Calculator!H48:H50"

# ── 6. Add missing node: Update Tracker with Rationale URL ───────────────────
# This runs after Save Rationale to Google Drive, before Merge Data for Email
update_tracker_rationale = {
    "id": "n14c_update_tracker_rationale",
    "name": "Update Tracker with Rationale URL",
    "type": "n8n-nodes-base.googleSheets",
    "typeVersion": 4,
    "position": [3770, 500],
    "parameters": {
        "operation": "update",
        "documentId": {"__rl": True, "value": SHEET_ID, "mode": "id"},
        "sheetName": {"__rl": True, "value": "Tracker", "mode": "name"},
        "columns": {
            "mappingMode": "defineBelow",
            "value": {
                "rationale_doc_url": "={{ 'https://docs.google.com/document/d/' + $input.first().json.id + '/edit' }}",
                "calculator_url":    f"=https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
            },
            "matchingColumns": ["engagement_id"],
            "schema": [
                {"id": "engagement_id",    "displayName": "engagement_id",    "required": False, "defaultMatch": True,  "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "rationale_doc_url","displayName": "rationale_doc_url","required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
                {"id": "calculator_url",   "displayName": "calculator_url",   "required": False, "defaultMatch": False, "display": True, "type": "string", "canBeUsedToMatch": True},
            ],
            "attemptToConvertTypes": False,
            "convertFieldsToString": False
        },
        "where": {
            "values": [{"column": "engagement_id", "condition": "equals", "conditionValue": "={{ $('Generate Engagement ID').first().json.engagementId }}"}]
        },
        "options": {}
    },
    "credentials": {"googleSheetsOAuth2Api": SHEET_CRED}
}

# Insert the new node
w['nodes'].append(update_tracker_rationale)

# ── 7. Rewire connections: Save Rationale → Update Tracker → Merge Data ───────
# Old: Save Rationale → Merge Data for Email
# New: Save Rationale → Update Tracker with Rationale URL → Merge Data for Email
conns = w['connections']
conns['Save Rationale to Google Drive'] = {
    "main": [[{"node": "Update Tracker with Rationale URL", "type": "main", "index": 0}]]
}
conns['Update Tracker with Rationale URL'] = {
    "main": [[{"node": "Merge Data for Email", "type": "main", "index": 0}]]
}

with open('D:/AIIR/n8n/workflow_1_transcript_pricing.json', 'w', encoding='utf-8') as f:
    json.dump(w, f, indent=2, ensure_ascii=False)

print('Done. Changes made:')
print('  1. Google Sheets credential updated to Tanmay (pQl0UnpSh855m4lW)')
print('  2. Sheet ID hardcoded:', SHEET_ID)
print('  3. Write to Tracker Sheet — schema + all 15 field mappings added')
print('  4. Write Calculator Cells — full batchUpdate body with 17 cell writes')
print('  5. Read Calculated Price — sheet ID updated')
print('  6. New node: Update Tracker with Rationale URL (rationale_doc_url + calculator_url)')
print('  7. Connections rewired: Save Rationale → Update Tracker → Merge Data')
