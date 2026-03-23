

# AIIR SOW System - Python Implementation

Complete rewrite of the AIIR Statement of Work generation system from n8n to Python/FastAPI.

**Status:** 🚧 In Development (Phase 1-2 Complete)

## Overview

This system automates the process of:
1. **Watching** for new discovery call transcripts in Google Drive
2. **Extracting** key variables using OpenAI GPT-4o
3. **Calculating** pricing using Megan Marshall's approved business logic
4. **Generating** SOW documents from templates
5. **Sending** for approval and archiving

## Architecture

- **Framework:** FastAPI (serverless-friendly)
- **Hosting:** Vercel (free tier)
- **AI:** OpenAI GPT-4o with structured outputs
- **Storage:** Google Drive + Google Sheets
- **State:** Upstash Redis
- **Email:** Gmail API

## Project Structure

```
aiir-sow-system/
├── api/                      # Vercel serverless functions
│   ├── webhooks/            # Webhook endpoints (approval buttons)
│   └── cron/                # Scheduled jobs (check for new transcripts)
│
├── app/                     # Core application logic
│   ├── business_logic/      # Pricing calculation, tier selection, etc.
│   │   ├── tier_selection.py          # Tier selection logic
│   │   ├── bill_rate.py               # Bill rate calculation
│   │   ├── threesixty_decision.py     # 360° KEEP/REDUCE/ELIMINATE logic
│   │   ├── reduction_hierarchy.py     # Megan's 6-lever budget reduction
│   │   └── pricing_calculator.py      # Orchestrates all business logic
│   │
│   ├── models/              # Pydantic data models
│   │   └── extracted_variables.py     # ExtractedVariables, CalculatedPricing, etc.
│   │
│   ├── services/            # External service integrations
│   │   ├── google_drive.py            # Google Drive API wrapper
│   │   ├── google_sheets.py           # Google Sheets API wrapper
│   │   ├── google_docs.py             # Google Docs API wrapper
│   │   ├── openai_service.py          # OpenAI GPT-4o extraction
│   │   ├── email_service.py           # Gmail API for emails
│   │   └── redis_service.py           # Upstash Redis state management
│   │
│   ├── workflows/           # Multi-step workflow orchestration
│   │   ├── workflow_1_pricing.py      # Transcript → Pricing + Review Email
│   │   ├── workflow_2_sow_generation.py  # Generate SOW from template
│   │   └── workflow_3_send_archive.py    # Send to client + Archive
│   │
│   ├── ai/                  # AI prompts and schemas
│   │   └── prompts.py                 # OpenAI structured output prompts
│   │
│   ├── utils/               # Utilities
│   └── config.py            # Configuration (loads from .env)
│
├── templates/               # Email templates (Jinja2)
├── tests/                   # Unit and integration tests
├── config/                  # Additional config files
│
├── .env                     # Environment variables (NOT in git)
├── .gitignore              # Git ignore file
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
├── test_business_logic.py   # Test script for business logic
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites

Install the following:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads/)
- **VS Code** (recommended) - [Download](https://code.visualstudio.com/)

### 2. Clone and Setup Project

```bash
# Navigate to AIIR directory
cd d:/AIIR

# The project is already created in: d:/AIIR/aiir-sow-system

# Navigate into project
cd aiir-sow-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

The `.env` file is already configured with your credentials:

- ✅ OpenAI API Key
- ✅ Google Service Account JSON path
- ✅ Google Drive/Sheets folder IDs
- ✅ Gmail configuration
- ✅ Upstash Redis credentials

**Important:** Make sure the Google Service Account has access to:
- Tracker Sheet: `1YpiNSVidnsp8fMQ0DOxE4SxC-NdjxwtksJz-9jYd0QM`
- All Google Drive folders (Transcripts, Rationales, SOW Templates, etc.)

### 4. Test Business Logic

Before building the full system, test the core business logic:

```bash
python test_business_logic.py
```

This will run 4 test cases:
1. ✅ Standard C-Suite engagement (no budget constraints)
2. ✅ Budget-constrained C-Suite (Megan's real $25k example)
3. ✅ Eliminate 360° (recent 360° completed)
4. ✅ Mid-level Director (ROADMAP tier)

**Expected Output:**
- Tier selections
- Bill rate calculations
- 360° decisions (KEEP/REDUCE/ELIMINATE)
- Budget reduction levers applied
- Total pricing
- Full rationale documents

## Business Logic Implementation

### ✅ Completed Logic

1. **Tier Selection**
   - Maps seniority level × engagement duration → Program tier
   - 6 tiers: IGNITE, ROADMAP, ASCENT, SPARK_I, SPARK_II, AIIR_VISTA

2. **Bill Rate Calculation**
   - Maps seniority × market type → Hourly rate
   - C-Suite: $600/hr (Mature), $500/hr (Emerging)
   - Senior: $500/hr (Mature), $400/hr (Emerging)
   - Mid-level: $400/hr (Mature), $350/hr (Emerging)
   - Early Career: $350/hr (Mature), $300/hr (Emerging)

3. **360° Interview Decision (Enhanced from Email Thread)**
   - **KEEP (6 hours):** Self-awareness or performance risk signals detected
     - Keywords: "self-awareness", "executive presence", "blind spots", "performance concerns", etc.
   - **ELIMINATE (0 hours):** Recent 360° already completed
     - Keywords: "just completed a 360", "last quarter", "already have feedback", etc.
   - **REDUCE (3-4 hours):** Budget signal but no strong development needs

4. **Megan's 6-Lever Budget Reduction Hierarchy**
   - **Trigger:** Budget ceiling mentioned or budget-sensitivity phrases
   - **Levers applied in order:**
     1. Stakeholder sessions: 1 hr → 0.75 hr
     2. Dev History: 2 hr → 1.5 hr
     3. 360° interviews: 6 hr → 4 hr (only if no strong development needs)
     4. Implementation sessions: subtract 1 session
     5. Dev Planning: remove if budget < $35k
     6. Assessment Feedback: 2 hr → 1.5 hr (last resort)

5. **Payment Terms Extraction**
   - Default: 100% upfront, Net 30 days
   - Detects: "Net 45", "50/50 split", "quarterly payments", etc.

### 🚧 In Progress

6. **Google API Services**
   - Google Drive: Upload, download, move files
   - Google Sheets: Read, write, update rows
   - Google Docs: Create from template, replace placeholders

7. **OpenAI Service**
   - Structured output extraction with enhanced keyword detection
   - All 40+ keywords from email thread analysis

8. **Workflows**
   - Workflow 1: Transcript → Pricing → Review Email
   - Workflow 2: Pricing Approved → Generate SOW
   - Workflow 3: SOW Approved → Send to Client → Archive

## Testing

### Unit Tests

```bash
pytest tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/
```

### Manual Testing

Use the test script to verify each component:

```bash
# Test business logic only (no API calls)
python test_business_logic.py

# Test Google API connection (coming soon)
python tests/test_google_apis.py

# Test OpenAI extraction (coming soon)
python tests/test_openai_extraction.py

# Test full workflow end-to-end (coming soon)
python tests/test_full_workflow.py
```

## Deployment (Future)

### Local Development

```bash
# Run FastAPI server locally
uvicorn api.index:app --reload --port 8000
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel deploy --prod
```

## Key Files Reference

### Configuration

- [`app/config.py`](app/config.py) - Central configuration, loads from `.env`
- [`.env`](.env) - Environment variables (Google credentials, API keys, folder IDs)

### Data Models

- [`app/models/extracted_variables.py`](app/models/extracted_variables.py) - All Pydantic models
  - `ExtractedVariables` - Variables extracted from transcript
  - `SessionHours` - Hours for each session type
  - `BudgetReduction` - Single budget reduction record
  - `CalculatedPricing` - Complete pricing calculation result
  - `EngagementRecord` - Full engagement record for Tracker sheet

### Business Logic

- [`app/business_logic/tier_selection.py`](app/business_logic/tier_selection.py) - Tier selection logic
- [`app/business_logic/bill_rate.py`](app/business_logic/bill_rate.py) - Bill rate calculation
- [`app/business_logic/threesixty_decision.py`](app/business_logic/threesixty_decision.py) - 360° decision with 40+ keywords
- [`app/business_logic/reduction_hierarchy.py`](app/business_logic/reduction_hierarchy.py) - Megan's 6-lever budget reduction
- [`app/business_logic/pricing_calculator.py`](app/business_logic/pricing_calculator.py) - Orchestrates all logic

### Analysis Documents

- [`BUSINESS_LOGIC_ANALYSIS.md`](../BUSINESS_LOGIC_ANALYSIS.md) - Complete business logic requirements extracted from email threads

## Email Thread Analysis

All business logic is based on email threads from Megan Marshall (March 2-6, 2026). Key insights:

1. **360° Decision Keywords** - Megan provided exact phrases for KEEP/ELIMINATE decisions
2. **6-Lever Hierarchy** - Sequential budget reduction approach with real example ($27,800 → $24,900)
3. **Budget Triggers** - Specific phrases that indicate budget sensitivity
4. **Payment Terms** - Extraction logic for Net 30/45, 50/50 splits, etc.

See [`BUSINESS_LOGIC_ANALYSIS.md`](../BUSINESS_LOGIC_ANALYSIS.md) for complete analysis.

## Development Roadmap

### Phase 1: Core Infrastructure ✅ COMPLETE
- [x] Configuration module
- [x] Data models with enhanced fields
- [x] Business logic modules
- [x] Test script

### Phase 2: Services (In Progress)
- [ ] Google Drive service
- [ ] Google Sheets service
- [ ] Google Docs service
- [ ] OpenAI service with enhanced prompts
- [ ] Gmail service
- [ ] Redis service

### Phase 3: Workflows
- [ ] Workflow 1: Transcript → Pricing
- [ ] Workflow 2: SOW Generation
- [ ] Workflow 3: Send & Archive

### Phase 4: API Endpoints
- [ ] FastAPI application setup
- [ ] Webhook endpoints (approval buttons)
- [ ] Cron job endpoint (check for new transcripts)

### Phase 5: Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual UAT with 3 test scripts (AEC, TST, Test Company)
- [ ] Deploy to Vercel
- [ ] Monitor and iterate

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Make sure you're running scripts from the `aiir-sow-system/` directory

**Issue:** `FileNotFoundError: [Errno 2] No such file or directory: '.env'`
- **Solution:** Make sure `.env` file exists in the project root

**Issue:** Google API authentication errors
- **Solution:** Verify the service account has access to all Google Drive folders and Sheets

## Support

For questions or issues:
1. Check this README
2. Review [`BUSINESS_LOGIC_ANALYSIS.md`](../BUSINESS_LOGIC_ANALYSIS.md)
3. Run `python test_business_logic.py` to verify core logic
4. Contact: kapurkartanmay@gmail.com

## License

Proprietary - AIIR Consulting

---

**Last Updated:** March 12, 2026
**Version:** 0.2.0 (Phase 1-2 Complete)
