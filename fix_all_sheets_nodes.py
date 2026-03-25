import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SHEET_ID   = '1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA'
SHEET_CRED = {'id': 'pQl0UnpSh855m4lW', 'name': 'Tanmay'}

# Full 27-column tracker schema
TRACKER_SCHEMA = [
    {'id': 'engagement_id',           'displayName': 'engagement_id',           'required': False, 'defaultMatch': True,  'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'created_at',              'displayName': 'created_at',              'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'transcript_filename',     'displayName': 'transcript_filename',     'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'client_company',          'displayName': 'client_company',          'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'coachee_name',            'displayName': 'coachee_name',            'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'hubspot_deal_id',         'displayName': 'hubspot_deal_id',         'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'coach_name',              'displayName': 'coach_name',              'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'tier',                    'displayName': 'tier',                    'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'bill_rate',               'displayName': 'bill_rate',               'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'num_participants',        'displayName': 'num_participants',        'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'price_per_participant',   'displayName': 'price_per_participant',   'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'total_engagement_price',  'displayName': 'total_engagement_price',  'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'payment_structure',       'displayName': 'payment_structure',       'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'net_days',                'displayName': 'net_days',                'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'pricing_approval_status', 'displayName': 'pricing_approval_status', 'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'pricing_approved_by',     'displayName': 'pricing_approved_by',     'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'pricing_approved_at',     'displayName': 'pricing_approved_at',     'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'rationale_doc_url',       'displayName': 'rationale_doc_url',       'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'calculator_url',          'displayName': 'calculator_url',          'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'sow_doc_url',             'displayName': 'sow_doc_url',             'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'sow_approval_status',     'displayName': 'sow_approval_status',     'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'sow_approved_by',         'displayName': 'sow_approved_by',         'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'sow_approved_at',         'displayName': 'sow_approved_at',         'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'client_email',            'displayName': 'client_email',            'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'sent_at',                 'displayName': 'sent_at',                 'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'archive_folder_url',      'displayName': 'archive_folder_url',      'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
    {'id': 'full_variables_json',     'displayName': 'full_variables_json',     'required': False, 'defaultMatch': False, 'display': True, 'type': 'string', 'canBeUsedToMatch': True},
]

def fix_sheets_node(node, value_map=None, matching_cols=None):
    """Apply correct sheet ID, credential, and schema to any Sheets node."""
    node['credentials'] = {'googleSheetsOAuth2Api': SHEET_CRED}
    node['parameters']['documentId'] = {'__rl': True, 'value': SHEET_ID, 'mode': 'id'}
    node['parameters']['sheetName']  = {'__rl': True, 'value': 'Tracker', 'mode': 'name'}
    if value_map is not None:
        node['parameters']['columns'] = {
            'mappingMode': 'defineBelow',
            'value': value_map,
            'matchingColumns': matching_cols or ['engagement_id'],
            'schema': TRACKER_SCHEMA,
            'attemptToConvertTypes': False,
            'convertFieldsToString': False
        }

# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW 2
# ═══════════════════════════════════════════════════════════════════════════════
with open('D:/AIIR/n8n/workflow_2_sow_generation.json', 'r', encoding='utf-8') as f:
    w2 = json.load(f)

for node in w2['nodes']:
    if 'googleSheets' not in node.get('type', ''):
        continue
    name = node['name']

    if name == 'Read Tracker Row':
        # Read node: just fix sheet ID + credential + filter
        fix_sheets_node(node)
        node['parameters']['operation'] = 'read'
        node['parameters']['filtersUI'] = {
            'values': [{'lookupColumn': 'engagement_id', 'lookupValue': '={{ $json.query.id }}'}]
        }
        node['parameters']['options'] = {'returnFirstMatch': True}
        del node['parameters']['columns']  # read nodes don't use columns

    elif name == 'Mark Pricing Approved in Tracker':
        fix_sheets_node(node, value_map={
            'pricing_approval_status': 'APPROVED',
            'pricing_approved_by':     'Reviewer (email link)',
            'pricing_approved_at':     '={{ new Date().toISOString() }}',
            'price_per_participant':   '={{ $json.pricePerParticipant }}',
            'total_engagement_price':  '={{ $json.totalEngagementPrice }}'
        })
        node['parameters']['operation'] = 'update'
        node['parameters']['where'] = {
            'values': [{'column': 'engagement_id', 'condition': 'equals',
                        'conditionValue': '={{ $json.engagement_id }}'}]
        }

    elif name == 'Update Tracker with SOW Link':
        fix_sheets_node(node, value_map={
            'sow_doc_url':         "={{ $('Store New Doc ID').first().json.newDocUrl }}",
            'sow_approval_status': 'PENDING'
        })
        node['parameters']['operation'] = 'update'
        node['parameters']['where'] = {
            'values': [{'column': 'engagement_id', 'condition': 'equals',
                        'conditionValue': "={{ $('Store New Doc ID').first().json.engagement_id }}"}]
        }

with open('D:/AIIR/n8n/workflow_2_sow_generation.json', 'w', encoding='utf-8') as f:
    json.dump(w2, f, indent=2, ensure_ascii=False)
print('Workflow 2 fixed')

# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW 3
# ═══════════════════════════════════════════════════════════════════════════════
with open('D:/AIIR/n8n/workflow_3_send_archive.json', 'r', encoding='utf-8') as f:
    w3 = json.load(f)

for node in w3['nodes']:
    if 'googleSheets' not in node.get('type', ''):
        continue
    name = node['name']

    if name == 'Read Tracker Row':
        fix_sheets_node(node)
        node['parameters']['operation'] = 'read'
        node['parameters']['filtersUI'] = {
            'values': [{'lookupColumn': 'engagement_id', 'lookupValue': '={{ $json.query.id }}'}]
        }
        node['parameters']['options'] = {'returnFirstMatch': True}
        if 'columns' in node['parameters']:
            del node['parameters']['columns']

    elif name == 'Mark SOW Approved in Tracker':
        fix_sheets_node(node, value_map={
            'sow_approval_status': 'APPROVED',
            'sow_approved_by':     'Reviewer (email link)',
            'sow_approved_at':     '={{ new Date().toISOString() }}'
        })
        node['parameters']['operation'] = 'update'
        node['parameters']['where'] = {
            'values': [{'column': 'engagement_id', 'condition': 'equals',
                        'conditionValue': '={{ $json.query.id }}'}]
        }

    elif name == 'Final Tracker Update':
        fix_sheets_node(node, value_map={
            'sent_at':             '={{ new Date().toISOString() }}',
            'archive_folder_url':  "={{ $('Collect Subfolder IDs').first().json.archiveFolderUrl }}"
        })
        node['parameters']['operation'] = 'update'
        node['parameters']['where'] = {
            'values': [{'column': 'engagement_id', 'condition': 'equals',
                        'conditionValue': "={{ $('Read Tracker Row').first().json.engagement_id }}"}]
        }

with open('D:/AIIR/n8n/workflow_3_send_archive.json', 'w', encoding='utf-8') as f:
    json.dump(w3, f, indent=2, ensure_ascii=False)
print('Workflow 3 fixed')
