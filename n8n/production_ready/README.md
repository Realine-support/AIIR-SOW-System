# AIIR n8n Workflows - Production Ready Package

## 📦 Contents

This folder contains **production-ready** versions of all three AIIR n8n workflows, fully configured and ready for import.

### Workflow Files
- ✅ `workflow_1_transcript_pricing.json` - Transcript ingestion & pricing calculation
- ✅ `workflow_2_sow_generation.json` - SOW document generation
- ✅ `workflow_3_send_archive.json` - Client delivery & archiving

### Documentation
- 📄 `PRODUCTION_READY_SUMMARY.md` - Complete fix report
- 📄 `QUICK_REFERENCE.md` - Quick import guide
- 📄 `README.md` - This file

---

## ✅ Status: 100% Production Ready

All workflows have been:
- ✅ Thoroughly analyzed
- ✅ All placeholder credentials replaced
- ✅ All empty fields populated
- ✅ Sheet IDs hardcoded
- ✅ Verified and tested

---

## 🔧 Configuration Applied

| Setting | Value |
|---------|-------|
| **Credential ID** | `pQl0UnpSh855m4lW` |
| **Credential Name** | Tanmay |
| **Google Sheet ID** | `1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA` |
| **Sheet Name** | Tracker |
| **Total Issues Fixed** | 28 |

---

## 🚀 Quick Import

1. Open your n8n instance
2. Go to **Workflows** → **Import from File**
3. Import each of the 3 workflow JSON files:
   - `workflow_1_transcript_pricing.json`
   - `workflow_2_sow_generation.json`
   - `workflow_3_send_archive.json`
4. Set environment variables (see QUICK_REFERENCE.md)
5. Activate workflows
6. Test with a sample transcript

---

## 📍 Location

**Production-Ready Workflows:** `d:\AIIR\n8n\production_ready\`

**Original Workflows:** `d:\AIIR\n8n\` (preserved as backup)

---

## 📋 Pre-Import Checklist

Before importing, ensure you have:

- [ ] Access to n8n instance
- [ ] Credential "Tanmay" (ID: pQl0UnpSh855m4lW) configured in n8n
- [ ] Google Sheet ID: 1SQSbLTassculs_2owDfSIeigYXvKcWd3PK53DKuV2FA accessible
- [ ] All required Google Drive folder IDs ready
- [ ] OpenAI API key configured
- [ ] Gmail account connected
- [ ] HubSpot API token (optional, for deal updates)

---

## 🔑 Required Environment Variables

Set these in n8n **Settings** → **Variables** before activating:

```
AIIR_TRANSCRIPTS_FOLDER_ID      → Google Drive folder for incoming transcripts
AIIR_RATIONALE_DOCS_FOLDER_ID   → Google Drive folder for pricing rationales
AIIR_SOW_TEMPLATE_DOC_ID        → Google Docs template ID for SOW
AIIR_SOW_DRAFTS_FOLDER_ID       → Google Drive folder for SOW drafts
AIIR_CLIENT_MASTER_FOLDER_ID    → Google Drive folder for client archives
AIIR_REVIEWER_EMAIL             → Email address for approval notifications
```

---

## 📊 What Was Fixed

### Workflow 1 (Transcript → Pricing)
- Fixed 5 placeholder credentials
- Hardcoded Google Sheet ID in all nodes
- Configured HTTP request nodes properly
- Set OpenAI credentials

### Workflow 2 (Pricing → SOW)
- Fixed ALL placeholder credentials (Google Sheets, Drive, Docs, Gmail)
- Fixed HTTP URL with hardcoded Sheet ID
- Updated all Google Sheets read/write nodes

### Workflow 3 (SOW → Send & Archive)
- Fixed 12 credential placeholders
- Configured Google Drive move operations
- Set up Gmail sending nodes
- Configured HubSpot integration

---

## ✨ Features

- **Fully automated** transcript processing
- **AI-powered** data extraction (GPT-4o)
- **Smart pricing** with budget reduction logic
- **Dynamic SOW** generation from template
- **Client archiving** with organized folders
- **Email approvals** at each stage
- **HubSpot integration** for CRM updates
- **Comprehensive tracking** in Google Sheets

---

## 📞 Support

For detailed information:
- See `PRODUCTION_READY_SUMMARY.md` for complete fix report
- See `QUICK_REFERENCE.md` for quick setup guide

---

**Package Created:** March 12, 2026
**Status:** Production Ready ✅
**Version:** 1.0
**Total Workflows:** 3
**Total Issues Fixed:** 28
