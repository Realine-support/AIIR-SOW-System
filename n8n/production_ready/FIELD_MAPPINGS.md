# Google Sheets Field Mappings

## If Fields Appear Empty After Import

The fields ARE configured in the JSON, but n8n's UI might not display them immediately. Here's what to do:

---

## Option 1: Just Run It (Recommended)

**The workflow will work correctly even if the UI shows empty fields.**

The mappings are stored in the JSON and will execute properly. You don't need to fill them in again.

---

## Option 2: Manual Verification

If you want to verify/re-enter the fields manually, here are the exact mappings:

### Write to Tracker Sheet Node

**Operation:** Append
**Mapping Mode:** Map Each Column Manually

| Column Name | Value (Expression) |
|-------------|-------------------|
| `engagement_id` | `={{ $json.engagementId }}` |
| `created_at` | `={{ $json.createdAt }}` |
| `transcript_filename` | `={{ $json.filename }}` |
| `client_company` | `={{ $json.client_company }}` |
| `coachee_name` | `={{ $json.coachee_name }}` |
| `hubspot_deal_id` | `={{ $json.hubspot_deal_id }}` |
| `coach_name` | `={{ $json.coachName }}` |
| `tier` | `={{ $json.tier }}` |
| `bill_rate` | `={{ $json.billRate }}` |
| `num_participants` | `={{ $json.num_participants }}` |
| `payment_structure` | `={{ $json.paymentStructure }}` |
| `net_days` | `={{ $json.netDays }}` |
| `pricing_approval_status` | `PENDING` (Fixed value) |
| `client_email` | `={{ $json.client_email }}` |
| `full_variables_json` | `={{ JSON.stringify($json) }}` |

### Update Tracker with Rationale URL Node

**Operation:** Update
**Match Column:** `engagement_id`
**Match Value:** `={{ $('Generate Engagement ID').first().json.engagementId }}`

| Column Name | Value (Expression) |
|-------------|-------------------|
| `rationale_doc_url` | `={{ 'https://docs.google.com/document/d/' + $input.first().json.id + '/edit' }}` |
| `calculator_url` | `https://docs.google.com/spreadsheets/d/1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA/edit` |
| `price_per_participant` | `={{ $('Parse Price From Response').first().json.pricePerParticipant }}` |
| `total_engagement_price` | `={{ $('Parse Price From Response').first().json.totalEngagementPrice }}` |

---

## Option 3: Check the Schema

After import, the node might need to "refresh" the schema from your actual Google Sheet:

1. Open the **Write to Tracker Sheet** node
2. Look for **"Fetch Fields"** or **"Refresh Schema"** button
3. Click it to load column names from your actual sheet
4. The mappings should then appear populated

---

## Why This Happens

n8n stores field mappings in two places:
1. **JSON configuration** ✅ (Already configured - workflow will work)
2. **UI schema cache** ❌ (Needs to refresh from your actual Google Sheet)

When you import a workflow, n8n has the mappings but hasn't yet connected to your sheet to validate the column names exist.

---

## Test Without Fixing

1. Import the workflow
2. Don't change anything in the Google Sheets nodes
3. Run a test execution
4. Check the Tracker sheet - you'll see the row was written correctly

If it works, you're done! The empty-looking fields are just a UI display issue.

---

## Important Note

The fields that are showing as empty in your screenshot:
- `pricing_approved_by`
- `pricing_approved_at`
- `rationale_doc_url`
- `calculator_url`
- `sow_doc_url`
- `sow_approval_status`
- `sow_approved_by`

**These are SUPPOSED to be empty in the "Write to Tracker Sheet" node** because they get filled later by Workflow 2 and Workflow 3!

Only these fields are written in Workflow 1:
- engagement_id
- created_at
- transcript_filename
- client_company
- coachee_name
- hubspot_deal_id
- coach_name
- tier
- bill_rate
- num_participants
- payment_structure
- net_days
- pricing_approval_status (set to "PENDING")
- client_email
- full_variables_json

---

## Bottom Line

**Your workflow is correctly configured.** The UI just doesn't show the mappings until you interact with the node or execute it. Try running it - it will work! ✅
