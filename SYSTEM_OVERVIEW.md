# AIIR SOW System - Complete Overview

## 🎯 What This System Does

This system **automatically processes discovery call transcripts** and generates pricing proposals for executive coaching engagements.

### Workflow (Simplified - No Emails)

```
1. Transcript uploaded to Google Drive
   ↓
2. System analyzes transcript with AI
   ↓
3. Calculates pricing based on business rules
   ↓
4. Updates Google Sheets with results
   ↓
5. Manual review in Google Sheets
   ↓
6. Update Status column: "Approved" or "Rejected"
```

---

## 📊 System Architecture

### Input
- **Discovery call transcripts** (.txt files) in Google Drive folder

### Processing
- **OpenAI GPT-4o** extracts variables from transcript
- **Business logic** calculates pricing based on:
  - Seniority level (C-Suite, Senior, Mid-level, etc.)
  - Market type (Mature vs Emerging)
  - Engagement duration
  - Budget constraints
  - 360° assessment needs

### Output
- **Google Sheets Tracker** with all engagement details
- **Google Sheets Calculator** with detailed pricing breakdown
- **Pricing Rationale** document in Google Drive

### Review Process
- **Manual review** in Google Sheets
- **Status column** tracks: "Pending Review", "Approved", "Rejected"

---

## 🔧 Business Logic Components

### 1. Tier Selection (`tier_selection.py`)
Selects coaching program tier based on:
- **Seniority Level**: C-Suite → IGNITE/ROADMAP, Senior → ASCENT, etc.
- **Duration**: 6-12 months → IGNITE, 4-6 months → ROADMAP, etc.
- **Advisory**: Special tier for advisors

**Program Tiers:**
- `IGNITE` - C-Suite, 6-12 months
- `ROADMAP` - C-Suite, 4-6 months
- `ASCENT` - Senior leaders
- `SPARK_I` / `SPARK_II` - Mid-level leaders
- `AIIR_VISTA` - Advisory coaching

### 2. Bill Rate Calculation (`bill_rate.py`)
Calculates hourly rate based on:
- **Seniority**: C-Suite ($550), Senior ($500), Mid-level ($400)
- **Market Type**: Emerging markets get 10% discount

**Examples:**
- C-Suite in Mature market: $550/hr
- C-Suite in Emerging market: $495/hr
- Senior in Mature market: $500/hr

### 3. 360° Assessment Decision (`threesixty_decision.py`)
Decides whether to include 360° interviews based on:

**KEEP (6 hours):**
- Strong self-awareness signals detected
- Keywords: "leadership brand", "executive presence", "how others perceive me", "blind spots"

**REDUCE (4 hours):**
- Budget constraints detected
- No strong development needs

**ELIMINATE (0 hours):**
- Client just completed 360° assessment
- Keywords: "just completed", "recent 360", "already have feedback"

### 4. Budget Reduction Hierarchy (`reduction_hierarchy.py`)
6-lever sequential reduction system (applied only when budget constraints detected):

**Lever 1**: Stakeholder sessions 1.0 hr → 0.75 hr
**Lever 2**: Dev History interview 2.0 hr → 1.5 hr
**Lever 3**: 360° interviews 6.0 hr → 4.0 hr (only if no strong development needs)
**Lever 4**: Implementation sessions subtract 1 session
**Lever 5**: Dev Planning removed if budget < $35k
**Lever 6**: Assessment feedback 2.0 hr → 1.5 hr (last resort)

**Budget Trigger Keywords:**
- "we've only used independent coaches before"
- "our benchmark is around $X"
- "that price feels high"
- "we do not pay over $X"
- "more cost-conscious"

### 5. Pricing Calculator (`pricing_calculator.py`)
Orchestrates all business logic:
1. Select tier
2. Get tier defaults
3. Calculate bill rate
4. Decide on 360° hours
5. Detect budget signals
6. Apply budget reductions if needed
7. Calculate final price
8. Generate rationale

---

## 📁 Google Sheets Structure

### Tracker Sheet (Main Record)

| Column | Field | Example |
|--------|-------|---------|
| A | Engagement ID | `TECHVISION-20260312-144500` |
| B | Client Company | `TechVision Inc.` |
| C | Coachee Name | `Michael Chen` |
| D | Coachee Title | `CTO` |
| E | Decision Maker | `Sarah Johnson` |
| F | Decision Maker Email | `sarah.johnson@techvision.com` |
| G | Program Tier | `IGNITE` |
| H | Seniority Level | `C-Suite` |
| I | Duration (months) | `6` |
| J | Market Type | `Mature` |
| K | Bill Rate | `550` |
| L | Total Hours | `32.5` |
| M | Total Price | `17875` |
| N | Payment Terms | `50% upfront, 50% at midpoint, Net 30` |
| O | Rationale URL | `https://docs.google.com/...` |
| P | Calculator URL | `https://docs.google.com/...` |
| Q | SOW URL | _(not generated yet)_ |
| **R** | **Status** | **`Pending Review`** → Update to `Approved` or `Rejected` |
| S | Created At | `2026-03-12T14:45:00` |
| T | Updated At | `2026-03-12T14:45:00` |

### Calculator Sheet (Detailed Breakdown)

| Column | Field | Example |
|--------|-------|---------|
| A | Engagement ID | `TECHVISION-20260312-144500` |
| B | Client Company | `TechVision Inc.` |
| C | Tier | `IGNITE` |
| D | Bill Rate | `550` |
| E | Implementation Sessions | `6` |
| F | Stakeholder Hours | `0.75` |
| G | Dev History Hours | `1.5` |
| H | 360° Hours | `0` |
| I | Assessment Feedback Hours | `2` |
| J | Total Price | `17875` |

---

## 🤖 AI Extraction (OpenAI)

The system uses **GPT-4o** with structured output to extract:

### Core Variables
- Client company name
- Coachee name, title, email
- Decision maker name, email, title
- Seniority level
- Engagement duration
- Market type

### Assessment Signals
- **Self-awareness signals**: Keywords indicating need for 360°
- **Existing 360° status**: If they already completed one

### Budget Signals
- **Budget ceiling**: Explicit max amount ("don't pay over $25k")
- **Budget constraint phrases**: Sensitivity indicators

### Special Flags
- **TES addon**: Team effectiveness requested
- **MSA rate card**: Existing contract rates
- **Custom template**: Client's own SOW format

### Context
- Development opportunities
- Success criteria
- Additional notes

---

## 🚀 How to Use This System

### Setup (One-Time)

1. **Upload sample transcript** to Google Drive:
   ```
   - Go to: https://drive.google.com/drive/folders/1JX0QUdZtxSn-1kEJrB1rwenJL9gjrWpu
   - Upload: sample_transcript.txt
   ```

2. **Run the test**:
   ```bash
   cd D:\AIIR\aiir-sow-system
   venv\Scripts\activate
   python test_simplified_workflow.py
   ```

3. **Check results**:
   - Open Google Sheets Tracker
   - See new row with engagement details
   - Review pricing, rationale, calculator
   - Update Status to "Approved" or "Rejected"

### Production Use

1. **Upload transcripts** to Transcripts folder in Google Drive
2. **System auto-processes** (via cron job every 5 minutes)
3. **Review in Google Sheets**:
   - Check pricing accuracy
   - Review AI-generated rationale
   - Verify session hours breakdown
4. **Update Status column**:
   - `Pending Review` → `Approved` (pricing looks good)
   - `Pending Review` → `Rejected` (needs manual adjustment)

---

## 📂 Key Files

### Workflows
- `app/workflows/workflow_1_pricing_simplified.py` - Main workflow (NO EMAILS)
- `app/workflows/workflow_1_pricing.py` - Old workflow (with emails) - DEPRECATED

### Business Logic
- `app/business_logic/pricing_calculator.py` - Orchestrates everything
- `app/business_logic/tier_selection.py` - Tier selection logic
- `app/business_logic/bill_rate.py` - Bill rate calculation
- `app/business_logic/threesixty_decision.py` - 360° decision logic
- `app/business_logic/reduction_hierarchy.py` - Budget reduction levers

### Services
- `app/services/google_drive.py` - Google Drive operations
- `app/services/google_sheets.py` - Google Sheets operations
- `app/services/google_docs.py` - Google Docs operations
- `app/services/openai_service.py` - OpenAI GPT-4o extraction
- `app/services/redis_service.py` - Redis state tracking

### Data Models
- `app/models/extracted_variables.py` - All data models

### API
- `api/index.py` - FastAPI application
- `api/cron/watch_transcripts.py` - Cron endpoint (checks for new transcripts)

### Configuration
- `.env` - Environment variables
- `app/config.py` - Configuration management

### Testing
- `test_simplified_workflow.py` - Test script
- `sample_transcript.txt` - Sample data

---

## 🎓 Business Logic Examples

### Example 1: Standard C-Suite Engagement

**Input:**
- Seniority: C-Suite
- Duration: 6 months
- Market: Mature
- Budget: No constraints
- Self-awareness signals: ["leadership brand", "executive presence"]

**Output:**
- Tier: IGNITE
- Bill Rate: $550/hr
- 360° Decision: KEEP (6 hours)
- Total Price: ~$27,800
- Budget Reductions: None

### Example 2: Budget-Constrained C-Suite

**Input:**
- Seniority: C-Suite
- Duration: 6 months
- Market: Mature
- Budget ceiling: $20,000
- Budget phrase: "our benchmark is around $18k"
- Self-awareness signals: None

**Output:**
- Tier: IGNITE
- Bill Rate: $550/hr
- 360° Decision: REDUCE (4 hours) - budget constraint
- Budget Reductions Applied:
  - Lever 1: Stakeholder 1.0 → 0.75 hr (-$137.50)
  - Lever 2: Dev History 2.0 → 1.5 hr (-$275)
  - Lever 3: 360° 6.0 → 4.0 hr (-$1,100) - no strong dev needs
  - Lever 4: Implementation 6 → 5 sessions (-$825)
- Total Price: ~$19,200 (within budget!)

### Example 3: Senior Leader, Recent 360°

**Input:**
- Seniority: Senior (VP level)
- Duration: 5 months
- Market: Mature
- 360° Status: "just completed 360 last month"

**Output:**
- Tier: ASCENT
- Bill Rate: $500/hr
- 360° Decision: ELIMINATE (0 hours) - recent assessment exists
- Total Price: ~$18,500
- Budget Reductions: None

---

## 🔍 Debugging & Logs

### View Logs
The workflow provides detailed logging at each step:
```
Step 1: Downloading transcript from Google Drive
Step 2: Extracting variables with OpenAI GPT-4o
Step 3: Calculating pricing with business logic
...
✓✓✓ WORKFLOW COMPLETED SUCCESSFULLY ✓✓✓
```

### Common Issues

**Issue**: No transcripts found
**Solution**: Upload .txt file to Transcripts folder in Google Drive

**Issue**: OpenAI API error
**Solution**: Check OPENAI_API_KEY in .env file

**Issue**: Google Sheets permission error
**Solution**: Make sure service account has edit access to sheets

**Issue**: Pricing seems wrong
**Solution**: Check business logic in rationale document, review budget constraints detected

---

## ✅ Next Steps

1. ✅ **Test with sample transcript** (sample_transcript.txt provided)
2. ✅ **Review results in Google Sheets**
3. ✅ **Verify pricing logic is accurate**
4. 🔄 **Upload real transcripts and test**
5. 🔄 **Refine business logic if needed**
6. 🔄 **Deploy to production (Vercel)**

---

## 📞 Support

For issues or questions:
- Check logs in terminal output
- Review `SYSTEM_OVERVIEW.md` (this file)
- Review `QUICK_OAUTH_FIX.md` for email setup (if needed later)
- Review business logic files for pricing calculations

---

## 🎉 Summary

**What works now:**
✅ Transcript analysis with AI
✅ Intelligent pricing calculation
✅ Budget reduction logic
✅ 360° assessment decision-making
✅ Google Sheets integration
✅ Manual review workflow via Status column

**What's removed:**
❌ Email notifications (too complex)
❌ Webhook approvals (not needed)
❌ OAuth complexity (not needed for sheets-only flow)

**Review process:**
1. System processes transcript → updates Google Sheets
2. Human reviews in Google Sheets
3. Human updates Status column to "Approved" or "Rejected"
4. Simple, clean, effective!
