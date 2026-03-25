# AIIR SOW Automation — n8n Setup Instructions

## Files in this folder
| File | Purpose |
|------|---------|
| `workflow_1_transcript_pricing.json` | Import into n8n — Workflow 1 |
| `workflow_2_sow_generation.json` | Import into n8n — Workflow 2 |
| `workflow_3_send_archive.json` | Import into n8n — Workflow 3 |
| `google_sheets_setup.js` | Google Apps Script — run once to build the Calculator sheet |
| `SETUP_INSTRUCTIONS.md` | This file |

---

## Step 1 — Google Drive Folder Structure

Create this folder structure in Google Drive manually (or via Drive UI):

```
AIIR SOW System/
├── 📁 Transcripts/          ← AIIR_TRANSCRIPTS_FOLDER_ID
├── 📁 SOW Templates/
│   └── AIIR_IGNITE_SOW_Template  ← AIIR_SOW_TEMPLATE_DOC_ID (Google Doc)
├── 📁 Rationale Docs/       ← AIIR_RATIONALE_DOCS_FOLDER_ID
└── 📁 Client Master Folder/ ← AIIR_CLIENT_MASTER_FOLDER_ID
```

For each folder, copy its ID from the URL:
`https://drive.google.com/drive/folders/THIS_IS_THE_ID`

---

## Step 2 — Google Sheets Pricing Calculator

1. Create a new Google Sheet: **"AIIR Pricing Calculator"**
2. Open **Extensions → Apps Script**
3. Paste the contents of `google_sheets_setup.js`
4. Run `setupAIIRPricingCalculator()`
5. Copy the Sheet ID shown in the confirmation dialog
   → This is your **`AIIR_PRICING_SHEET_ID`**

### After setup, manually verify:
- `Calculator!B16` = `0.65` (Margin — must NEVER be 0.70)
- `Calculator!F38` = `75` (IGNITE CZ Rate — must be $75, not $50)
- `Calculator!H50` formula = `=IF(H49="",H48,H48*H49)` (total price)
- `Tracker` sheet has all 27 header columns (A through AA)

---

## Step 3 — Google Docs SOW Template

1. Upload `Client A.EC.Jonathan Bailey.docx` to Google Drive
2. Right-click → **Open with Google Docs** (converts to Google Doc)
3. **Replace all variable content** with these exact `{{PLACEHOLDER}}` tokens:

| Location | Find/Replace |
|----------|-------------|
| Header ID field | Replace deal ID with `{{HUBSPOT_ID}}` |
| Footer ID field | Replace deal ID with `{{HUBSPOT_ID}}` |
| Stakeholder count ("four") | Replace with `{{STAKEHOLDER_COUNT}}` |
| Coach name | Replace with `{{COACH_NAME}}` |
| "client" / "coachee" | Replace with `{{CLIENT_TERM}}` |
| Dev History duration ("2-hour") | Replace with `{{DEV_HISTORY_TEXT}}` |
| 360° interview count ("up to 8 confidential interviews") | Replace with `{{INTERVIEW_COUNT}}` |
| "three streams" / "two streams" | Replace with `{{STREAMS_COUNT}}` |
| Assessment Feedback duration sentence | Replace with `{{ASSESSMENT_FEEDBACK_TEXT}}` |
| Dev Planning row text | Replace with `{{DEV_PLANNING_TEXT}}` |
| Total price (e.g., "$47,475") | Replace with `{{TOTAL_PRICE}}` |
| Payment structure sentence | Replace with `{{PAYMENT_STRUCTURE}}` |
| Net days (e.g., "30") | Replace with `{{NET_DAYS}}` |
| Client company (policy paragraph 1) | Replace with `{{CLIENT_COMPANY}}` |
| Client company (policy paragraph 2) | Replace with `{{CLIENT_COMPANY}}` |
| Client company (signature block) | Replace with `{{CLIENT_COMPANY}}` |

> ⚠️ IMPORTANT: Remove any client-specific data (Jonathan Bailey, etc.) — the template must be generic.
> ⚠️ DO NOT replace the boilerplate legal/policy paragraphs — those stay as-is.

4. Save the doc
5. Copy the Google Doc ID from the URL: `https://docs.google.com/document/d/THIS_IS_THE_ID/edit`
   → This is your **`AIIR_SOW_TEMPLATE_DOC_ID`**

6. Move the doc to `AIIR SOW System/SOW Templates/`

---

## Step 4 — n8n Credentials

In your n8n instance (https://primary-production-bd72.up.railway.app/):

Go to **Settings → Credentials** and note the IDs for:

| Credential | Used by |
|------------|---------|
| Google Drive OAuth2 | All 3 workflows |
| Google Sheets OAuth2 | All 3 workflows |
| Google Docs OAuth2 | Workflow 2 |
| Gmail OAuth2 | Workflows 1, 2, 3 |
| OpenAI API | Workflow 1 |

For HubSpot (when ready):
- Create a new credential: **HTTP Header Auth**
- Name: `HubSpot Bearer Token`
- Header Name: `Authorization`
- Header Value: `Bearer YOUR_HUBSPOT_PRIVATE_APP_TOKEN`

---

## Step 5 — Set n8n Workflow Variables

For each workflow, after importing, go to:
**Workflow → Settings → Variables** (or via the workflow header)

Set these variables:

| Variable | Value |
|----------|-------|
| `AIIR_REVIEWER_EMAIL` | Megan's email (or team reviewer) |
| `AIIR_PRICING_SHEET_ID` | From Step 2 |
| `AIIR_SOW_TEMPLATE_DOC_ID` | From Step 3 |
| `AIIR_TRANSCRIPTS_FOLDER_ID` | From Step 1 |

> Note: n8n workflow variables are accessed as `$vars.VARIABLE_NAME` in expressions.
> If your n8n version doesn't support workflow variables, use Set nodes at the start of each workflow.

---

## Step 6 — Import Workflows into n8n

1. In n8n, click **+** (Add Workflow) → **Import from file**
2. Import `workflow_1_transcript_pricing.json`
3. Import `workflow_2_sow_generation.json`
4. Import `workflow_3_send_archive.json`

For each imported workflow:
1. Open each node that shows a credential warning
2. Select the correct credential from your n8n credential list
3. Update any hardcoded folder IDs (search for `AIIR_*_FOLDER_ID` in node parameters)

### Nodes requiring manual updates after import:

**Workflow 1:**
- `Save Rationale to Google Drive` → update `folderId` to `AIIR_RATIONALE_DOCS_FOLDER_ID`
- `Merge Data for Email` → update `AIIR_PRICING_SHEET_ID_PLACEHOLDER` in the code
- All credential fields → select your actual credentials

**Workflow 2:**
- `Copy SOW Template` → update `folderId` to `AIIR_RATIONALE_DOCS_FOLDER_ID`
- All credential fields → select your actual credentials

**Workflow 3:**
- `Create Client SOWs Folder` → update `folderId` to `AIIR_CLIENT_MASTER_FOLDER_ID`
- All credential fields → select your actual credentials

---

## Step 7 — Update HTTP Request URLs

In Workflows 1 and 2, the HTTP Request nodes use `{{$vars.AIIR_PRICING_SHEET_ID}}` in the URL.
n8n expressions in URLs use `={{ }}` syntax. After import, verify these URLs look like:

```
https://sheets.googleapis.com/v4/spreadsheets/={{ $vars.AIIR_PRICING_SHEET_ID }}/values:batchUpdate
```

If workflow variables aren't supported, hardcode the Sheet ID directly.

---

## Step 8 — Test Each Workflow

### Unit Test — Workflow 1:
1. Create a test transcript file `test_transcript.txt` with this content:
```
Meeting Notes — Discovery Call
Client: Acme Corporation
Coachee: Jane Smith, Senior Vice President
Market: US (Mature)
Duration: 9 months
Budget: approximately $45,000
No previous 360 assessment completed.
Self-awareness noted as development area.
Payment: 100% upfront preferred.
Contact: jane.smith@acme.com
```
2. Upload to `AIIR SOW System/Transcripts/` in Google Drive
3. Wait up to 1 minute for Workflow 1 to trigger
4. Check n8n execution log — verify all nodes green
5. Verify pricing review email arrives in reviewer inbox
6. Check Google Sheet Tracker — row should appear with status PENDING

### Unit Test — Workflow 2:
1. Click the **APPROVE PRICING** link in the test email
2. Browser should show "✅ Pricing Approved" confirmation page
3. Check n8n — Workflow 2 should execute
4. Verify SOW Google Doc was created with all placeholders replaced
5. Verify SOW review email arrives
6. Check Tracker — pricing_approval_status = APPROVED

### Unit Test — Workflow 3:
1. Click **APPROVE SOW & SEND TO CLIENT** link in SOW review email
2. Verify client email is sent (or manual send flag if no email)
3. Verify files moved to `Client Master Folder/Acme Corporation/`
4. Verify Tracker — sow_approval_status = APPROVED, sent_at populated

---

## Key Assertions (Verify These)

After a full end-to-end run, check:

| Assertion | How to verify |
|-----------|---------------|
| B16 = 0.65 in Sheets | Open Calculator sheet, cell B16 |
| Payment = "100% invoiced upon program kickoff" | Check SOW doc + email |
| "Jonathan Bailey" nowhere in output | Search SOW doc |
| "Client A" nowhere in output | Search SOW doc |
| Coach = "a Senior Level AIIR Consultant" (if no chem call) | Check SOW doc |
| 360° min = 5 interviews | Check reduction logic in WF1 execution |
| IGNITE CZ Rate = $75 | Check F38 in Calculator sheet |

---

## Troubleshooting

### Workflow 1 not triggering
- Confirm Google Drive Trigger is **Active** (toggle in top-right of workflow)
- Verify folder ID is correct — trigger watches a specific folder
- Check that the file is uploaded to the exact `Transcripts/` folder, not a subfolder

### AI Agent output parsing fails
- The AI Agent with Structured Output Parser outputs to `$json.output` (already a parsed object)
- The `Tier Selection + Bill Rate` code node reads `$input.first().json.output`
- Check that the OpenAI Chat Model sub-node is connected to the AI Agent via `ai_languageModel` (not "main")
- Check that Structured Output Parser is connected via `ai_outputParser` (not "main")
- Verify OpenAI credential is valid and has available credits

### Google Sheets "batchUpdate" 401 error
- The HTTP Request node uses `predefinedCredentialType: googleSheetsOAuth2Api`
- Make sure the Google Sheets OAuth2 credential has Sheets API scope enabled
- Re-authorize the credential if needed

### Google Docs placeholder not replaced
- Verify placeholders in template use exact format `{{PLACEHOLDER}}` (double curly braces)
- Check the batchUpdate request in WF2 node `Replace All Placeholders in SOW`
- Run the node in test mode and check the request body sent

### "Client email not found" email received
- Normal behavior — the fallback node flags it for manual send
- Add client email to transcript text, or manually update the Tracker sheet

---

## Critical Rules (Must Never Be Violated)

1. **Margin B16 = 0.65 always** — the code in WF1 Node 11 hardcodes `0.65`
2. **IGNITE CZ Rate = $75** — set in `google_sheets_setup.js` at F38
3. **Payment default = 100% upfront** — set in WF1 Node 8 (Payment Terms)
4. **Net days default = 30** — set in WF1 Node 8
5. **360° floor = 5 interviews** — enforced in WF1 Node 7 (Reduction Hierarchy)
6. **SPARK I has NO Dev History Interview** — B39 = 0 for SPARK_I tier
7. **Assessment Feedback: 2hrs → DELETE sentence; 1.5hrs → ADD sentence** — in WF2 Node 5
8. **CLIENT_COMPANY replaces in 3 locations** — handled by `{{CLIENT_COMPANY}}` token x3 in template
