# AIIR Consulting — SOW Automation System
## Complete Project Context & Build Specification

> **Purpose of this document:** This file is the single source of truth for building the AIIR SOW Automation System. It contains complete context, business logic, data structures, workflow rules, error corrections, and implementation instructions. A developer with zero prior knowledge of this project should be able to read this document and fully understand what to build and how.

---

## Table of Contents

1. [Project Overview & Business Context](#1-project-overview--business-context)
2. [The People Involved](#2-the-people-involved)
3. [What We Are Building — System Summary](#3-what-we-are-building--system-summary)
4. [Source Files & Their Roles](#4-source-files--their-roles)
5. [The Complete 15-Step System Flow](#5-the-complete-15-step-system-flow)
6. [Coaching Tier Selection Logic — All 6 Tiers](#6-coaching-tier-selection-logic--all-6-tiers)
7. [Excel Pricing Calculator — Complete Cell Map](#7-excel-pricing-calculator--complete-cell-map)
8. [Budget Signal Detection & Reduction Hierarchy](#8-budget-signal-detection--reduction-hierarchy)
9. [360° Interview Sub-Decision Logic](#9-360-interview-sub-decision-logic)
10. [Payment Terms Detection Logic](#10-payment-terms-detection-logic)
11. [SOW Template — Complete Field Map (All 17 Comments)](#11-sow-template--complete-field-map-all-17-comments)
12. [Bill Rate Detection Logic](#12-bill-rate-detection-logic)
13. [All Keyword & Signal Lists](#13-all-keyword--signal-lists)
14. [Known Errors & Corrections in Source Files](#14-known-errors--corrections-in-source-files)
15. [Data Extraction Specification — What to Pull From a Transcript](#15-data-extraction-specification--what-to-pull-from-a-transcript)
16. [Human Review Checkpoints](#16-human-review-checkpoints)
17. [Archiving & CRM Update Logic](#17-archiving--crm-update-logic)
18. [Implementation Notes & Constraints](#18-implementation-notes--constraints)

---

## 1. Project Overview & Business Context

### What is AIIR Consulting?

AIIR Consulting is an executive coaching firm. They deliver structured coaching engagements to business leaders at various seniority levels — from early-career managers up to C-Suite executives. Their engagements are sold as fixed-scope packages with a defined set of coaching sessions, psychometric assessments, and stakeholder interviews.

### What is an SOW?

An SOW (Statement of Work) is a formal contract document that AIIR sends to a client company before an engagement begins. It describes:
- What sessions will be delivered and in what format
- Which assessments will be administered
- The total price of the engagement
- Payment terms
- Cancellation and confidentiality policies
- Signature blocks for both parties

Every engagement gets a unique SOW. Currently, a human (Megan Marshall, Managing Partner) manually creates each SOW by filling in an Excel pricing calculator first, then editing a Word template. This project automates that process.

### The Problem Being Solved

Currently the workflow is:
1. A sales or partner call happens with a prospective client
2. Someone manually reads the meeting transcript
3. They manually open the Excel pricing calculator and fill in the right cells
4. They manually edit the Word SOW template with the right numbers, names, and terms
5. The SOW goes out to the client

This is slow, error-prone, and requires deep institutional knowledge. The goal is to replace steps 2-4 with an AI agent that reads the transcript and does all of this automatically, requiring only human review before sending.

### Who Asked for This to Be Built?

Andrew Line, CEO of RE ALINE (a consulting and operations firm), is building this system on behalf of AIIR Consulting. He recorded a Zoom meeting with Megan Marshall (AIIR's Managing Partner) where she walked through the entire pricing logic live in the Excel file. Andrew documented every rule in the Excel file as cell-level comments. The source files contain all this institutional knowledge.

---

## 2. The People Involved

| Name | Role | Relevance |
|------|------|-----------|
| **Megan Marshall** | Managing Partner, AIIR Consulting | The subject matter expert. She defines all pricing logic, reduction rules, and SOW standards. Her words (via Zoom transcript) are the authority on all business rules. |
| **Andrew Line** | CEO, RE ALINE | The project commissioner. He translated Megan's Zoom walkthrough into Excel comments and is building this automation system. He also left comments in the SOW template flagging every variable field. |
| **Jonathan Bailey** | Example Coach | The coach named in the sample SOW (Client A EC Jonathan Bailey.docx). This is the template file used as the base for all IGNITE SOWs. |
| **Jonathan Kirschner** | Named Coach (in SOW boilerplate) | The specific coach referenced in the template as an example. The AI must replace this name with the actual assigned coach — or leave a placeholder if no coach has been confirmed yet. |

---

## 3. What We Are Building — System Summary

The system is a **fully automated SOW generation pipeline** with two human review checkpoints. Here is the complete end-to-end flow at a high level:

```
[Client Meeting Transcript Uploaded]
          ↓
[AI reads transcript and extracts key variables]
          ↓
[AI selects the correct coaching tier]
          ↓
[AI sets bill rate based on market type + seniority]
          ↓
[AI detects budget constraints → applies reduction hierarchy if needed]
          ↓
[AI writes correct values into Excel pricing calculator]
[Excel auto-calculates total price]
          ↓
[AI detects payment terms signals]
          ↓
[AI generates a pricing summary with rationale]
          ↓
[HUMAN REVIEW #1: Team reviews pricing in Excel]
          ↓
[AI populates the SOW Word template with all variables]
          ↓
[HUMAN REVIEW #2: Team reviews full SOW]
          ↓
[SOW sent to client, archived, HubSpot updated]
```

**The two things the AI produces:**
1. A filled-in Excel pricing calculator (all relevant cells written with correct values)
2. A populated SOW Word document (all placeholder variables replaced with real data, all conditional text updated based on pricing decisions)

---

## 4. Source Files & Their Roles

### 4.1 Excel Pricing Calculator

**Filename:** `MASTER_of_Bespoke_Integrated_Solutions_Costing_Calculator_v1.xlsx`

**Sheets:**
- `Coaching Calculator` — The primary sheet. Contains 6 separate coaching tier sections, each with their own rows and cells. All pricing logic lives here.
- `Costing Calculator - Integrated` — A combined/integrated view. Less frequently edited directly.
- `Deliverable Glossary` — Reference definitions for each deliverable type. Not directly edited.

**Important note on the Excel file:** The file has Andrew's comments on many cells documenting what Megan said in the Zoom about that specific cell. These comments are the primary source of truth for default values, minimums, and reduction rules.

### 4.2 SOW Word Template

**Filename:** `Client_A_EC_Jonathan_Bailey.docx`

This is a real SOW that was already filled in for a client called "Client A" (Jonathan Bailey as the coachee). Andrew has added **17 comments** throughout the document flagging every single field that the AI must update or be careful about. Some fields are static and must NEVER be changed. Others are dynamic and must be updated based on transcript signals and pricing decisions.

**Tier:** This SOW is an IGNITE tier engagement. The same template structure applies to other tiers but the specific session names and counts differ.

### 4.3 Email Thread (from Andrew to Megan — March 6, 2026)

This email is the source of:
- The complete 360° keep vs. reduce vs. eliminate keyword lists
- Megan's confirmation of the reduction hierarchy priority order
- Payment term defaults
- Notes on the "three streams of data" SOW language

### 4.4 Zoom/Loom Recording Transcript (Megan's Walkthrough)

This is a recording of Megan walking through the Excel file live, explaining every row. It is the source of:
- All default values and minimum values in the Excel file
- Megan's exact language about when to reduce each session type
- The CZ fee rate correction ($75, not $50)
- The margin correction (65%, not 70%)
- The 360° interview minimum (hard floor of 5)
- Megan's confirmation that the Development Planning Session can be fully removed in severe cases

---

## 5. The Complete 15-Step System Flow

### Step 1: Trigger

A new transcript file is uploaded to a designated Google Drive folder. Supported formats: `.txt`, `.docx`, `.pdf`. The upload triggers the automation pipeline.

**Failure handling:** If the file is unreadable, empty, or not a transcript format, the system must immediately alert the team via email/Slack and stop. No further processing should occur.

---

### Step 2: Ingest & Parse Transcript

The system reads the transcript file and converts it to clean plain text for NLP processing.

- Remove timestamps, speaker labels (e.g., "[00:02:15] John:") while preserving the content
- Concatenate all text into a single string for analysis
- Flag if transcript appears to be very short (< 500 words) as potentially incomplete

---

### Step 3: Extract Core Variables (NLP Extraction)

The AI must extract the following variables from the transcript. Each variable is documented with what to look for and what to do if not found.

| Variable | What to Look For | If Not Found |
|----------|-----------------|--------------|
| **Client company name** | Company being coached, sponsor company | Flag for human to fill |
| **Coachee name** | The individual being coached | Flag for human to fill |
| **HubSpot Deal ID** | Any mention of a deal number, ID, or reference number | Leave blank, flag |
| **Coach name** | Assigned AIIR coach | Only use if post-chemistry call confirmed (see Step 5 logic) |
| **Leadership seniority level** | Explicit or implied seniority (VP, Director, C-Suite, early career, etc.) | Use duration as proxy |
| **Market type** | Country or region of client company | Default to Mature if unclear |
| **Engagement duration** | Number of months mentioned ("6-month program", "nine months", etc.) | Use tier default |
| **Number of participants** | How many coachees are being enrolled | Default to 1, flag |
| **Budget signals** | Any cost constraint language (see Section 13) | None = no reduction needed |
| **Existing 360/assessment status** | Mention of recent 360, prior assessments | Default = no prior data |
| **Payment preference** | Any mention of payment structure or net terms | Use defaults |
| **Client terminology** | Does client say "client" or "coachee" when referring to the person being coached? | Default to "client" |
| **Chemistry call status** | Has a chemistry call with the coach been completed? | Default = not yet |

---

### Step 4: Select Coaching Tier

Based on extracted seniority and duration signals, select one of the 6 tiers. Each tier has completely different session structures — not just different hours. The full tier details are in Section 6.

**Decision logic:**

```
IF seniority = C-Suite AND duration ≥ 10 months → ASCENT
ELSE IF seniority = Senior/Director/VP AND duration 6-9 months → IGNITE
ELSE IF seniority = Mid-level/Manager AND duration 4-6 months → ROADMAP
ELSE IF seniority = Early Career AND duration 3-4 months → SPARK I
ELSE IF seniority = Early Career AND duration 4-5 months → SPARK II
ELSE IF type = Executive Advisory/On-Demand → AIIR VISTA (6 or 12 months)
```

If signals conflict or are ambiguous, flag for human clarification before proceeding.

---

### Step 5: Determine Coach Name for SOW

**Rule:** Only insert the real coach's name in the SOW if the transcript confirms a chemistry call has already been completed and a coach has been formally selected.

- If **chemistry call complete + coach assigned** → Insert coach's actual name
- If **chemistry call not yet done** → Insert: `"a Senior Level AIIR Consultant"`
- The default in the template is "Jonathan Kirschner" — this must always be replaced

---

### Step 6: Set Bill Rate (Excel Cell B15)

Bill rate is a **manual input** — it is not auto-calculated. The AI must detect both the market type and the seniority level from the transcript, then write the appropriate rate to cell `B15`. Full logic in Section 12.

---

### Step 7: Set Margin (Excel Cell B16)

**Always write `0.65` (65%) to cell B16.**

⚠️ **Critical correction:** The Excel file currently shows `0.70` (70%) in cell B16. Andrew's comment on that cell explicitly states: *"Megan's zoom, she has 65% (not 70%), and she said this is very standard."* The file is wrong. The AI must always override this to `0.65`.

---

### Step 8: Budget Signal Detection

Scan the full transcript for budget constraint keywords (see Section 13.1 for the complete keyword list).

- **If no budget signals detected:** Use all default hours for the selected tier. Skip to Step 10.
- **If budget signals detected:** Extract the target budget amount if stated explicitly. Then proceed to the reduction hierarchy (Step 9).

---

### Step 9: Apply Reduction Hierarchy

If budget constraints were detected, apply Megan's reduction levers in strict priority order. Each lever has a default and a minimum. Never go below the minimum. Stop reducing once the price target is met.

Full hierarchy details in Section 8. The 360° decision has its own sub-logic in Section 9.

---

### Step 10: Write Values to Excel

For the selected tier, write all determined values to their specific Excel cells. The participant count (`E49` for IGNITE, varies by tier) is always blank in the template and **must be written first** because the total engagement price (`H50`) depends on it.

After writing, Excel auto-calculates:
- Total coaching hours
- Total coach cost
- PM fee (12%)
- Total services cost
- Total services including margin
- Engagement total per participant
- Total for the full engagement

The AI reads the final calculated price from the total engagement cell (see Section 7 for which cell per tier).

---

### Step 11: Detect Payment Terms

Scan transcript for payment structure and net-day signals (see Section 10). Apply defaults if no signals found.

**Default (always apply unless overridden):**
- Payment structure: 100% upfront at kickoff
- Net days: 30 days

⚠️ **Critical correction:** The default is NOT 50/50. The 50/50 split only applies when a client has explicitly negotiated it. The existing template SOW shows 50/50 because that specific client negotiated it — it is NOT the standard.

---

### Step 12: Generate Pricing Summary

Produce a human-readable pricing rationale document including:
- Selected tier and why
- Bill rate and which market/seniority level was detected
- Whether budget constraints were detected and which keywords triggered them
- Every reduction made — which lever, what changed (original → new value), and the impact on price
- Whether the 360° was reduced or eliminated and why
- Payment terms applied
- Final price per participant and total engagement price

This document accompanies the Excel file for the human reviewer.

---

### Step 13: Human Review — Pricing

A team member reviews the AI-generated pricing in Excel, reads the rationale document, and either:
- **Approves:** Triggers SOW generation
- **Adjusts:** Manually modifies cells, re-approves

This is a required checkpoint. SOW generation cannot begin until pricing is explicitly approved.

---

### Step 14: Populate SOW Template

Using the approved pricing and all extracted variables, populate the SOW Word template. Full field-by-field rules in Section 11.

Key principle: Some fields must NEVER be changed (boilerplate text, policies). Others must ALWAYS be updated. Others are conditional. The rules in Section 11 are exhaustive.

---

### Step 15: Human Review — SOW, Send, Archive

A team member reviews the complete SOW draft. Edits directly if needed. Upon approval:
1. Send SOW to client via email or DocuSign
2. Archive to the client's master Google Drive folder with standardized filename
3. Update HubSpot deal status

---

## 6. Coaching Tier Selection Logic — All 6 Tiers

Each tier has a structurally different set of sessions. They are NOT interchangeable. The differences between tiers are fundamental — different session types, different CZ rates, different 360° mechanisms.

---

### 6.1 IGNITE — Senior Leaders (6–9 Months)

**Target:** Senior leaders, typically Director to VP level  
**Duration:** 6–9 months  
**CZ Months (E37):** Variable — extract from transcript. Range: 7–9 months  
**CZ Rate (F37):** $75/month  
**Default Total Hours:** 23–23.5 hrs  
**Minimum Total Hours:** 17.25 hrs  

**Sessions (Coaching Calculator rows):**

| Row | Session Name | Cell | Default Hours | Minimum Hours | Notes |
|-----|-------------|------|---------------|---------------|-------|
| B37 | Initial Coaching Session | B37 | 0.5 hr | 0.5 hr (fixed) | Never changes. First meeting between coach and coachee. |
| B38 | Stakeholder 1: Agenda Setting Meeting (ASM) | B38 | 1.0 hr | 0.5 hr (30 min) | Lever 1 for reduction |
| B39 | Developmental History Interview | B39 | 2.0 hrs | 1.5 hrs (90 min) | Lever 2. Deep background session. |
| B40 | Interview-Based 360° Assessment | B40 | =(45×8)/60 = 6 hrs | =(45×5)/60 = 3.75 hrs | Lever 3. Formula-driven. Hard floor: 5 interviews. |
| B41 | Assessment Feedback Session | B41 | 2.0 hrs | 1.5 hrs (90 min) | Lever 6 (last resort). Review of all assessment data. |
| B42 | Development Planning Session | B42 | 1.0 hr | 0 hrs (fully removable) | Lever 5. Can be completely removed in severe cases. |
| B43 | Stakeholder 2: Presentation of SDP | B43 | 1.0 hr | 0.5 hr (30 min) | Lever 1 |
| B44 | Implementation Sessions | B44 | 8.0 hrs (8×1hr) | 7.0 hrs (7 sessions) | Lever 4. Reduce COUNT only, never reduce per-session duration. |
| B45 | Stakeholder 3: Mid-Point Check-In | B45 | 1.0 hr | 0.5 hr (30 min) | Lever 1. Can be removed if total count drops to 3. |
| B46 | Stakeholder 4: Wrap-Up Session | B46 | 1.0 hr | 0.5 hr (30 min) | Lever 1 |

**Assessments (right-side columns):**

| Cell | Item | Default Quantity | Rate | Notes |
|------|------|-----------------|------|-------|
| E37 | Coaching Zone Fee months | 7–9 (extract from transcript) | F37 = $75 | Variable CZ months |
| E38 | LD12 360° | 0 | — | **IGNITE does NOT include LD12 360°.** Uses interview-based 360° instead. |
| E39 | LD12 | 1 | ~$150 | Standard inclusion |
| E40 | Hogan Insight | 1 | ~$300 | = 3 bundled assessments: HPI + HDS + MVPI |
| E41 | TES (Team Effectiveness Survey) | 0 (blank) | ~$300 | Optional. Include only if team effectiveness survey is in scope. |
| E49 | **Number of Participants** | **BLANK — must be written** | — | ⚠️ Critical. Always blank in template. AI must populate from transcript. |

**Price calculation chain (IGNITE):**
```
B47 = SUM(B37:B46)          → Total coaching hours
B48 = B47 × B15             → Total coach cost (hours × bill rate)
B49 = B48 × 0.12            → PM fee (12% of coach cost)
B50 = B48 + B49             → Total services cost (without margin)
H44 = SUM(G37:G43)          → Total assessments & fees per participant
H47 = B50 ÷ (1 − B16)      → Total services including margin (B16 = 0.65)
H48 = SUM(H42:H47)          → Engagement total PER PARTICIPANT ← per-person price
H50 = H48 × E49             → TOTAL FOR ENGAGEMENT (all participants) ← SOW price
```

**SOW price cell:** `H50` (if multiple participants) or `H48` (if single participant, since H50 = H48 × 1)

---

### 6.2 ROADMAP — Mid-Level Leaders (4–6 Months)

**Target:** Mid-level managers  
**Duration:** 4–6 months  
**CZ Months (E21):** 6  
**CZ Rate (F21):** $75/month  

**Key structural differences from IGNITE:**
- Dev History Interview is **1.5 hrs** by default (not 2 hrs)
- **Includes LD12 360°** (E22 = 1) — uses a survey-based LD12 360° instead of interview-based 360°
- Only **5 implementation sessions** (not 8)
- Only **3 stakeholder meetings** (no Mid-Point check-in)

**Price cells:** Engagement Total Per Participant = `H30`, Total for Engagement = `H32` (= H30 × E31), Participants = `E31`

---

### 6.3 ASCENT — C-Suite Leaders (10–12 Months)

**Target:** C-Suite executives  
**Duration:** 10–12 months  
**CZ Months (E55):** 12  
**CZ Rate (F55):** **$50/month** ← Different from other tiers which use $75

**Key structural differences from IGNITE:**
- CZ rate is **$50/month** (not $75)
- **12 implementation sessions** (not 8)
- 360° is interview-based but calculated for **12 interviews**: `=(45×12)/60 = 9 hrs`
- All 4 stakeholder meetings included (same as IGNITE)
- Dev History = 2 hrs (same as IGNITE)
- Bill rate for C-Suite: $600/hr mature, $500/hr emerging

**Price cells:** Engagement Total Per Participant = `H66`, Total for Engagement = `H68` (= H66 × E67), Participants = `E67`

---

### 6.4 SPARK I — Early Career Leaders (3–4 Months)

**Target:** Early career / junior managers  
**Duration:** 3–4 months  
**CZ Months (E73):** 4  
**CZ Rate (F73):** $75/month  

**Key structural differences — SPARK I is fundamentally different:**
- ⚠️ **NO Developmental History Interview** (coaching session) — instead uses a **Developmental History Survey** (E77 = $60 flat fee assessment — not a coached session)
- ⚠️ **NO interview-based 360°** — uses **Survey-based 360°** (E75 = $350 flat fee assessment)
- Only **3 implementation sessions** (not 8)
- Only **2 stakeholder meetings** (Agenda Setting + Wrap-Up only — no SDP presentation, no Mid-Point)
- Stakeholder sessions are **0.5 hr each** (not 1 hr)
- Assessment Feedback Session = **1.5 hrs** (not 2 hrs)

**Sessions:**

| Row | Session Name | Cell | Default Hours |
|-----|-------------|------|---------------|
| B73 | Initial Coaching Session | B73 | 0.5 hr |
| B74 | Stakeholder 1: Agenda Setting Meeting | B74 | 0.5 hr |
| B75 | Assessment Feedback Session | B75 | 1.5 hrs |
| B76 | Development Planning Session | B76 | 1.0 hr |
| B77 | 3 Implementation Sessions | B77 | 3.0 hrs |
| B78 | Stakeholder 2: Wrap-Up Session | B78 | 0.5 hr |

**Assessments (SPARK I):**

| Cell | Item | Default Qty | Rate |
|------|------|------------|------|
| E73 | Coaching Zone Fee months | 4 | $75 |
| E74 | LD12 | 1 | $150 |
| E75 | Survey-based 360° | 1 | $350 (flat fee) |
| E76 | Hogan Insight | 1 | $300 |
| E77 | Developmental History Survey | 1 | $60 (flat fee) |

**Price cells:** Engagement Total Per Participant = `H82`, Total for Engagement = `H84` (= H82 × E83), Participants = `E83`

---

### 6.5 SPARK II — Early Career Leaders (4–5 Months)

**Target:** Early career leaders (slightly more senior than SPARK I)  
**Duration:** 4–5 months  
**CZ Months (E91):** 5  
**CZ Rate (F91):** $75/month  

**Key structural differences from SPARK I:**
- **Has** a Developmental History Interview, but only **1.0 hr** (not 2 hrs, not interview-based at IGNITE level)
- Uses **Survey-based 360°** (same as SPARK I — not interview-based)
- **5 implementation sessions** (not 3 like SPARK I, not 8 like IGNITE)
- **3 stakeholder meetings** (adds SDP presentation back vs. SPARK I)
- Stakeholder sessions are **0.5 hr each**
- Assessment Feedback = **1.5 hrs**

**Sessions:**

| Row | Session Name | Cell | Default Hours |
|-----|-------------|------|---------------|
| B91 | Initial Coaching Session | B91 | 0.5 hr |
| B92 | Stakeholder 1: Agenda Setting Meeting | B92 | 0.5 hr |
| B93 | Developmental History Interview | B93 | 1.0 hr |
| B94 | Assessment Feedback Session | B94 | 1.5 hrs |
| B95 | Development Planning Session | B95 | 1.0 hr |
| B96 | Stakeholder 2: Presentation of SDP | B96 | 0.5 hr |
| B97 | 5 Implementation Sessions | B97 | 5.0 hrs |
| B98 | Stakeholder 3: Wrap-Up Session | B98 | 0.5 hr |

**Price cells:** Engagement Total Per Participant = `H100`, Total for Engagement = `H102` (= H100 × E101), Participants = `E101`

---

### 6.6 AIIR VISTA — Executive Advisory (6 or 12 Months)

**Target:** Senior executives, advisory/on-demand coaching model  
**Duration:** 6 months OR 12 months (two separate sections in Excel)  
**CZ Rate:** **$50/month** ← Same as ASCENT, different from other tiers

**Key structural differences:**
- First session is called **"Kick-off Meeting"** (not "Initial Coaching Session")
- Dev History Interview = **3.0 hrs** (longer than all other tiers)
- Uses interview-based 360° (same as IGNITE/ASCENT)
- CZ rate is $50/month (not $75)
- Two separate Excel sections: VISTA 6 months and VISTA 12 months

**VISTA 6-Month Section:**

| Row | Session Name | Cell | Default Hours |
|-----|-------------|------|---------------|
| B107 | Kick-off Meeting | B107 | 0.5 hr |
| B108 | Stakeholder 1: Agenda Setting Meeting | B108 | 1.0 hr |
| B109 | Developmental History Interview | B109 | 3.0 hrs |
| B110 | Interview-based 360° (up to 8 interviews) | B110 | =(45×8)/60 = 6 hrs |
| B111 | Assessment Feedback Session | B111 | 2.0 hrs |
| B112 | Development Planning Session | B112 | 1.0 hr |
| B113 | Stakeholder 2: Presentation of SDP | B113 | 1.0 hr |
| B114 | Implementation Sessions | B114 | 8.0 hrs |
| B115 | Stakeholder 3: Mid-Point Check-In | B115 | 1.0 hr |
| B116 | Stakeholder 4: Wrap-Up Session | B116 | 1.0 hr |

**VISTA 6-month price cells:** Engagement Total Per Participant = `H118`, Total for Engagement = `H120` (= H118 × E119), Participants = `E119`

**VISTA 12-month price cells:** Engagement Total Per Participant = `H136`, Total for Engagement = `H138` (= H136 × E137), Participants = `E137`

---

### Tier Quick Reference

| Tier | Target | Duration | CZ Months | CZ Rate | Impl. Sessions | Stakeholder Mtgs | 360° Type |
|------|--------|----------|-----------|---------|----------------|------------------|-----------|
| IGNITE | Senior | 6–9 mo | 7–9 | $75 | 8 | 4 | Interview-based (8×45min) |
| ROADMAP | Mid-level | 4–6 mo | 6 | $75 | 5 | 3 | LD12 Survey 360° |
| ASCENT | C-Suite | 10–12 mo | 12 | $50 | 12 | 4 | Interview-based (12×45min) |
| SPARK I | Early career | 3–4 mo | 4 | $75 | 3 | 2 | Survey-based ($350 flat) |
| SPARK II | Early career | 4–5 mo | 5 | $75 | 5 | 3 | Survey-based |
| AIIR VISTA | Advisory | 6 or 12 mo | 6 or 12 | $50 | 8 | 4 | Interview-based (8×45min) |

---

## 7. Excel Pricing Calculator — Complete Cell Map

### 7.1 Global Input Cells (Apply to All Tiers)

| Cell | Field | Default | Correct Value | Notes |
|------|-------|---------|---------------|-------|
| **B15** | Coaching Bill Rate ($/hr) | $350 | Varies by market + seniority | AI must detect and write. See Section 12. |
| **B16** | Margin | 0.70 in file | **0.65 (CORRECT VALUE)** | ⚠️ File has wrong value. ALWAYS write 0.65. |

### 7.2 IGNITE Section — Full Cell Reference

**Session Hours (Column B):**

| Cell | Session | Default | Min | Lever | Reduction Rule |
|------|---------|---------|-----|-------|----------------|
| B37 | Initial Coaching Session | 0.5 | 0.5 (fixed) | None | Never change |
| B38 | Stakeholder 1: ASM | 1.0 | 0.5 (30 min) | 1st | Reduce under any budget pressure |
| B39 | Dev History Interview | 2.0 | 1.5 (90 min) | 2nd | Never go below 90 min |
| B40 | Interview-Based 360° | =(45×8)/60 | =(45×5)/60 | 3rd | Formula: =(interviews×45)/60. Floor: 5 interviews |
| B41 | Assessment Feedback | 2.0 | 1.5 (90 min) | 6th (last) | Megan strongly resists cutting. Floor: 90 min |
| B42 | Dev Planning Session | 1.0 | 0.0 (removable) | 5th | Can be fully removed. Megan usually keeps it. |
| B43 | Stakeholder 2: SDP | 1.0 | 0.5 (30 min) | 1st | Same rule as other stakeholder sessions |
| B44 | Implementation Sessions | 8.0 (8×1hr) | 7.0 (7 sessions) | 4th | Reduce COUNT only. Never shorten per-session duration. |
| B45 | Stakeholder 3: Midpoint | 1.0 | 0.5 (30 min) | 1st | Can be removed if total count drops to 3 |
| B46 | Stakeholder 4: Wrap-Up | 1.0 | 0.5 (30 min) | 1st | |

**Assessment Quantities (Column E):**

| Cell | Item | Default | Notes |
|------|------|---------|-------|
| E37 | CZ Fee months | 9 (max) | Extract from transcript. Range 7–9 for IGNITE. |
| E38 | LD12 360° quantity | 0 | IGNITE does NOT use LD12 360°. Always 0. |
| E39 | LD12 quantity | 1 | Standard. Remove only if client opts out. |
| E40 | Hogan Insight quantity | 1 | = HPI + HDS + MVPI bundled |
| E41 | TES quantity | blank (0) | Optional. Only add if team effectiveness survey in scope. |
| **E49** | **# of Participants** | **BLANK** | **⚠️ Must be written. Drives total price calculation.** |

**Assessment Rates (Column F):**

| Cell | Item | Rate |
|------|------|------|
| F37 | CZ Fee rate | $75/month |
| F39 | LD12 rate | ~$150 |
| F40 | Hogan Insight rate | ~$300 |
| F41 | TES rate | ~$300 |

**Auto-Calculated Totals (DO NOT WRITE — these are Excel formulas):**

| Cell | Formula | Description |
|------|---------|-------------|
| B47 | =SUM(B37:B46) | Total coaching hours |
| B48 | =B47×B15 | Total coach cost |
| B49 | =B48×0.12 | PM fee (12%) |
| B50 | =B48+B49 | Total services cost (without margin) |
| H44 | =SUM(G37:G43) | Total assessments & fees per participant |
| H47 | =B50÷(1−B16) | Total services including margin |
| H48 | =SUM(H42:H47) | **Engagement Total Per Participant** |
| **H50** | =H48×E49 | **TOTAL FOR ENGAGEMENT ← This is the SOW price** |

---

## 8. Budget Signal Detection & Reduction Hierarchy

### 8.1 Budget Signal Detection

Scan the transcript for any of the keywords/phrases in Section 13.1. If detected:
1. Note which phrase was detected (include in rationale)
2. If a specific dollar amount is mentioned, extract it as the budget target
3. Proceed to the reduction hierarchy
4. Stop reducing once calculated price meets or falls below the budget target

### 8.2 Reduction Hierarchy — IGNITE (Primary Reference)

Apply levers in this exact order. Never skip a lever. Never go below minimums.

---

**LEVER 1: Stakeholder Sessions — Reduce First**

- **Applies to:** B38, B43, B45, B46 (all 4 stakeholder meetings)
- **Default:** 1.0 hr each
- **Step 1 reduction:** 45 minutes each
- **Maximum reduction (floor):** 30 minutes each — Megan's exact words: *"That's about as low as I would go, for these stakeholder meetings."*
- **Trigger:** Any budget constraint signal
- **SOW impact:** If Midpoint (B45) is fully removed (count drops to 3 total): update program description paragraph from "four formal stakeholder meetings" → "three formal stakeholder meetings"
- **Note:** The Development Planning Session (B42) is NOT a stakeholder session despite being near those rows. It has different rules.

---

**LEVER 2: Developmental History Interview — Second**

- **Applies to:** B39
- **Default:** 2.0 hrs
- **Maximum reduction (floor):** 1.5 hrs (90 minutes) — Megan's exact words: *"I try not to go lower than 90 minutes."*
- **Trigger:** Budget constraint remains after Lever 1 insufficient
- **SOW impact:** If reduced to 90 min, update SOW table row for Dev History Interview: change "2-hour" → "90-minute" OR remove the duration mention entirely (Megan's preference — she sometimes just deletes the duration text rather than updating it)
- **Note:** SPARK I does NOT have this session at all — it uses a $60 survey instead

---

**LEVER 3: Interview-Based 360° Assessment — Third (with sub-logic)**

- **Applies to:** B40 (IGNITE, ASCENT, VISTA only — other tiers use different 360° types)
- **Default:** 8 interviews × 45 min = 6.0 hrs [formula: =(45×8)/60]
- **Maximum reduction (floor):** 5 interviews × 45 min = 3.75 hrs [formula: =(45×5)/60]
- **Hard floor:** 5 interviews. Megan's exact words: *"I'm not gonna go lower than 5, typically."*
- **Trigger:** Budget constraint + NO self-awareness/leadership-brand signals in transcript
- **Sub-logic:** See Section 9 for full decision tree

---

**LEVER 4: Implementation Sessions — Fourth**

- **Applies to:** B44
- **Default:** 8 sessions × 1 hr = 8.0 hrs
- **Maximum reduction:** 7 sessions × 1 hr = 7.0 hrs (minimum 7 sessions)
- **Rule:** ONLY reduce the COUNT of sessions. NEVER shorten the per-session duration from 1 hour.
- **Trigger:** Budget constraint remains after Levers 1–3 insufficient
- **SOW impact:** Update "8 executive coaching sessions" → "7 executive coaching sessions" in the deliverables table

---

**LEVER 5: Development Planning Session — Last Resort A**

- **Applies to:** B42
- **Default:** 1.0 hr
- **Maximum reduction:** Can be fully removed (minimum = 0 hrs)
- **Note:** Megan's exact words: *"In severe cases, I might remove this, but I tend to always keep it."*
- **Trigger:** Budget constraint remains after Levers 1–4 insufficient
- **SOW impact:**
  - If reduced to 30 min: update "1-hour session" → "30-minute session" in table
  - If fully removed (set to 0): remove the entire Development Planning Session row from the SOW deliverables table

---

**LEVER 6: Assessment Feedback Session — Last Resort B**

- **Applies to:** B41
- **Default:** 2.0 hrs
- **Maximum reduction (floor):** 1.5 hrs (90 minutes) — Megan's exact words: *"I try not to cut down. The lowest I would go is 90 minutes."*
- **Trigger:** Absolute last resort. Budget constraint remains after Levers 1–5 insufficient
- **SOW impact:**
  - If still at 2.0 hrs (unchanged): **delete the duration sentence entirely** from the SOW table ("This meeting is typically two-hours in duration." → remove this sentence)
  - If reduced to 1.5 hrs: update the duration text to "90-minute"
  - ⚠️ This is the opposite of what you'd expect: if it's the DEFAULT value (2 hrs), delete the mention. If it's reduced, update the mention. Andrew's comment 9 explicitly states this.

---

## 9. 360° Interview Sub-Decision Logic

This logic applies when a budget constraint has been detected AND you are evaluating whether to reduce Lever 3 (the interview-based 360°).

### Decision Tree

```
STEP 1: Scan transcript for KEEP signals (see Section 13.2)
   └─ IF any KEEP signal found → KEEP full 360° (all 8 interviews)
      Do NOT reduce even if budget constraint exists.
      The 360° is critical for self-awareness development.

STEP 2 (only if no KEEP signals): Scan transcript for ELIMINATE signals (see Section 13.3)
   └─ IF any ELIMINATE signal found (client already has recent 360 data)
      → SET B40 = 0 (eliminate entirely)
      → Remove the Interview-Based 360° row from the SOW deliverables table
      → Update Stage II text: "three streams of data" → "two streams of data"
         (The three streams are: 360° data, psychometric results, and Dev History Interview.
          Removing 360° leaves two: psychometric results + Dev History Interview.)

STEP 3 (only if no KEEP and no ELIMINATE signals):
   → If budget constraint exists: REDUCE count from 8 toward minimum of 5
   → If no budget constraint: Keep at default (8 interviews)
```

### Reduction Formula

When reducing interview count, use the formula: `=(number_of_interviews × 45) / 60`

Examples:
- 8 interviews: =(45×8)/60 = 6.0 hrs
- 7 interviews: =(45×7)/60 = 5.25 hrs
- 6 interviews: =(45×6)/60 = 4.5 hrs
- 5 interviews: =(45×5)/60 = 3.75 hrs ← hard floor

### SOW Updates When 360° Count Changes

If the interview count changes, update the SOW deliverables table text:
- Default text: "up to 8 confidential interviews"
- If reduced to 6: "up to 6 confidential interviews"
- If reduced to 5: "up to 5 confidential interviews"
- If eliminated entirely: remove the Interview-Based 360° row completely

### Types of 360° by Tier

| Tier | 360° Type | Mechanism | Cell | Notes |
|------|-----------|-----------|------|-------|
| IGNITE | Interview-Based | Coach conducts interviews | B40 | 8 interviews default, 5 minimum |
| ROADMAP | LD12 360° Survey | Assessment survey | E22 = 1 | Not a coached session — flat fee |
| ASCENT | Interview-Based | Coach conducts interviews | B58 | 12 interviews default |
| SPARK I | Survey-Based 360° | Assessment | E75 = $350 | Not a coached session — flat fee |
| SPARK II | Survey-Based 360° | Assessment | E93 | Not a coached session — flat fee |
| AIIR VISTA | Interview-Based | Coach conducts interviews | B110 | 8 interviews default |

---

## 10. Payment Terms Detection Logic

### 10.1 Payment Structure

**Default (apply when no signal detected):** 100% upfront at kickoff

⚠️ This is the most important correction in this project. The existing template SOW shows a 50/50 split only because that specific client negotiated it. The AI must always default to 100% upfront and only change this if there is an explicit signal.

| Signal Detected | Apply |
|----------------|-------|
| No signal | 100% invoiced upon kickoff |
| "50-50" / "50/50" / "split payment" / "two installments" | 50% at kickoff + 50% at month 3 |
| "milestone" / "stage-based" | Stage-based invoicing (discuss structure with team) |
| "three installments" / "quarterly" | Three-part structure (flag for human to define) |

### 10.2 Net Payment Days

**Default (apply when no signal detected):** 30 days

| Signal Detected | Apply | Note |
|----------------|-------|------|
| No signal | 30 days | Default |
| "net 45" / "45 days" / "forty-five days" | 45 days | ⚠️ Requires CFO approval first |
| "net 30" / "30 days" | 30 days | Standard |
| "net 60" / "60 days" | 60 days | Flag for approval |

---

## 11. SOW Template — Complete Field Map (All 17 Comments)

The SOW template has 17 fields flagged by Andrew's comments. Each is documented below with the exact rule for what to do.

### Understanding the Comment Numbering

Andrew numbered his comments 0-16. The comments are ordered by their position in the document. "Comment [N]" refers to the Nth comment in the document as numbered by Andrew.

---

### Header Section

**Comment [0] — Header ID Number**
- **Location:** `ID#: 395830485039589` in the document header
- **Rule:** Replace with the HubSpot Deal ID extracted from transcript
- **If no HubSpot ID found:** Leave as placeholder and flag for human

**Comment [1] — Footer ID Number**
- **Location:** Same ID# in the document footer
- **Rule:** Replace with the same HubSpot Deal ID
- **Note:** Same value as Comment [0] — must be updated in BOTH header AND footer

---

### Program Description Section

**Comment [2] — Boilerplate Intro Paragraph**
- **Location:** The first main program description paragraph ("Ignite is a four-phase executive coaching program...")
- **Rule:** ⛔ **NEVER CHANGE THIS PARAGRAPH.** Megan explicitly stated this boilerplate never changes. No variables, no edits, no exceptions.

**Comment [3] — Stakeholder Meeting Count**
- **Location:** The phrase "four formal stakeholder meetings" in the program description paragraph
- **Rule:**
  - Default (4 stakeholder meetings): leave as "four formal stakeholder meetings"
  - If count reduced to 3: change to "three formal stakeholder meetings"
  - Megan's exact words: "I would never really cut down less than 3." Never go below 3 in the text.

**Comment [4] — Coach Name**
- **Location:** "delivered by Jonathan Kirschner..." in the program description
- **Rule:**
  - If chemistry call is complete and coach is assigned: insert coach's real name
  - If chemistry call not yet done: use "a Senior Level AIIR Consultant"
  - The template has "Jonathan Kirschner" — this MUST always be replaced with one of the above

**Comment [5] — Client/Coachee Terminology**
- **Location:** "Coach and client meet..." in the Coaching Kickoff description row
- **Rule:** Default is "client." If transcript shows the client consistently uses "coachee," update all instances throughout the document. Detect from how the sponsoring company refers to the individual being coached in the call.

---

### Deliverables Table — Stage I: Assessment

**Comment [6] — Developmental History Interview Duration**
- **Location:** The "Developmental History Interview" row in the deliverables table
- **Rule:**
  - If B39 = 2.0 hrs (unchanged): either delete the duration mention entirely OR leave the "2-hour" text (Megan's preference is to delete the duration mention in many cases)
  - If B39 = 1.5 hrs (reduced to 90 min): update text to "90-minute Developmental History Interview"
  - ⚠️ Megan sometimes simply removes the hour reference rather than updating it

**Comment [7] — Interview-Based 360° Interview Count**
- **Location:** "up to 8 confidential interviews" in the 360° row
- **Rule:**
  - If B40 = 6 hrs (8 interviews, unchanged): leave as "up to 8"
  - If B40 reduced (e.g., 6 interviews): update to "up to 6"
  - If B40 = 0 (eliminated): remove this entire table row

---

### Deliverables Table — Stage II: Integration and Analysis

**Comment [8] — "Three Streams of Data" Text**
- **Location:** Stage II: Integration and Analysis of Data description row
- **Exact default text:** Something like "...integration and analysis of three streams of data (360° interview data, psychometric results, and Developmental History Interview)..."
- **Rule:**
  - If 360° is present: leave as "three streams of data"
  - If 360° is eliminated (B40 = 0): change to "two streams of data" and remove the 360° item from the parenthetical list
  - This update must happen whenever the 360° elimination decision is made

**Comment [9] — Assessment Feedback Session Duration**
- **Location:** Assessment Feedback Session row in deliverables table
- **Rule (this is counterintuitive):**
  - If B41 = 2.0 hrs (default, unchanged): **delete the sentence that mentions the duration** entirely. The sentence typically reads something like "This meeting is typically two-hours in duration." Delete the whole sentence.
  - If B41 = 1.5 hrs (reduced to 90 min): **update** the duration text to "90-minute"
  - Reason: The 2-hour mention creates an expectation that is not always met, so Megan prefers to remove it when it's the default

**Comment [10] — Development Planning Session Duration**
- **Location:** Development Planning Session row in deliverables table
- **Rule:**
  - If B42 = 1.0 hr (unchanged): leave text as is
  - If B42 reduced (e.g., to 30 min): update "1-hour" → "30-minute" in the row text
  - If B42 = 0 (removed): remove the entire Development Planning Session row from the table

---

### Professional Fees & Payment Terms Section

**Comment [11] — Total Engagement Price**
- **Location:** "The Ignite coaching program is offered for $27,445" (or similar price statement)
- **Rule:** Replace price with value from Excel cell `H50` (Total for Engagement = Engagement Total Per Participant × Number of Participants)
- **If single participant:** H50 = H48 × 1 = H48. Price = H48.
- **If multiple participants:** Price = H50.
- This is a **1:1 direct mapping.** The price in the SOW must exactly match what Excel shows in H50.

**Comment [12] — Payment Structure**
- **Location:** The sentence describing when invoices are issued
- **Default text to use:** "100% invoiced upon program kickoff"
- **If 50/50 negotiated:** "50% invoiced upon program kickoff. 50% invoiced three months following program kickoff."
- ⚠️ The current template shows 50/50 because that was negotiated for Client A. The DEFAULT for new SOWs is 100% upfront.

**Comment [13] — Payment Net Days**
- **Location:** "Payments are due within 45 days" (or 30 days)
- **Default:** "Payments are due within 30 days of receipt of invoice"
- **If 45 days negotiated (requires CFO approval):** "Payments are due within 45 days of receipt of invoice"

---

### Policies & Signature Block

**Comment [14] — Client Name (First Instance in Policy)**
- **Location:** First occurrence of "Client A" in the payment policy paragraph
- **Rule:** Replace "Client A" with the actual client company name extracted from transcript
- **Exact context:** Something like "...AIIR is not responsible for any payment processing fees or taxes incurred by [Client A]..."

**Comment [15] — Client Name (Second Instance in Policy)**
- **Location:** Second occurrence of "Client A" in the same or adjacent policy paragraph
- **Rule:** Replace "Client A" with the actual client company name
- **Note:** This is a separate replacement from Comment [14] — both must be updated

**Comment [16] — Client Name in Signature Block**
- **Location:** "Client A" on the right side of the signature block
- **Rule:** Replace "Client A" with the actual client company name
- **Note:** This is the third separate replacement. Total = 3 client name replacements across the full document.

---

### Summary: Always vs. Conditional vs. Never

| Category | Fields | Rule |
|----------|--------|------|
| **NEVER change** | Boilerplate intro paragraph, Cancellation Policy, Confidentiality Policy | Static — no exceptions |
| **ALWAYS change** | Header/footer ID, Client name (3 locations), Coach name, Total price, Payment terms | Always dynamic |
| **Conditionally change** | Stakeholder count text, Dev History duration, 360° count/presence, Assessment Feedback sentence, Dev Planning duration, "three streams" vs "two streams" | Depends on pricing decisions |

---

## 12. Bill Rate Detection Logic

Cell `B15` is a manual input that the AI must set. It cannot be auto-calculated. The AI must detect both the client's market type AND the coachee's seniority level from the transcript.

### 12.1 Market Type Detection

**Mature Market** (higher rates):
- United States, Canada, United Kingdom, Western Europe, Australia, New Zealand, Singapore, Japan

**Emerging Market** (lower rates):
- Latin America (Mexico, Brazil, Colombia, etc.)
- Eastern Europe
- Africa
- Middle East (excluding UAE)
- Southeast Asia (excluding Singapore)
- India

**If unclear:** Default to Mature market and flag for human review.

### 12.2 Bill Rate Table

| Seniority Level | Mature Market | Emerging Market |
|----------------|---------------|-----------------|
| Tier 1 (Senior/Director/VP) | $350/hr | $300/hr |
| Tier 2 (Mid-level/Manager) | $250/hr | $200/hr |
| C-Suite (CEO/COO/CFO/CTO/CPO/President) | $600/hr | $500/hr |

**Default in file:** $350/hr (Tier 1, Mature market)

### 12.3 Seniority-to-Tier Mapping

| Title/Level Mentioned | Tier |
|----------------------|------|
| Manager, Senior Manager, Team Lead, early career | Tier 2 |
| Director, Senior Director, VP, SVP, Principal | Tier 1 |
| C-Suite (CEO, COO, CFO, CTO, CHRO, President, EVP, Group VP) | C-Suite |

---

## 13. All Keyword & Signal Lists

### 13.1 Budget Constraint Keywords

Any of the following phrases in the transcript triggers the reduction hierarchy:

- "too expensive"
- "too costly"
- "budget is $X" / "our budget is"
- "cap at $X" / "capped at"
- "we typically pay around $X"
- "that price feels high"
- "more cost-conscious"
- "we do not pay over $X"
- "need to come down in cost" / "come down on price"
- "outside our usual range"
- "our benchmark is $X"
- "we've only used independent coaches"
- "like your offering, but..."
- "we need something more accessible"
- "that's above what we budgeted"
- "we're working with a tighter budget"
- "budget constraints"
- "price point is a concern"

### 13.2 360° KEEP Signals (Do NOT reduce even under budget pressure)

Any of the following in the transcript means the 360° is strategically critical and must be preserved:

- "self-awareness"
- "leadership brand"
- "executive presence"
- "how others experience them" / "how others perceive them"
- "stakeholder perception"
- "blind spots"
- "needs honest feedback"
- "needs broader perspective"
- "reputation internally"
- "influence with stakeholders"
- "performance concerns"
- "feedback from the team hasn't been great"
- "communication or presence issues"
- "needs to work on stakeholder relationships"
- "some performance concerns"
- "perception gap"
- "doesn't know how they come across"
- "others see them differently"

### 13.3 360° ELIMINATE Signals (Client already has recent 360 data)

Any of the following means a recent 360 is already available — eliminate it from the scope:

- "just completed a 360"
- "already have feedback from the organization"
- "went through a 360 last quarter" / "recent 360"
- "we can share their previous assessment"
- "we already have feedback"
- "they already have assessment data"
- "360 was done recently"
- "we have their 360 results"

### 13.4 Payment Structure Signals

- Default (no signal): 100% upfront
- "50-50" / "50/50" → Split payment
- "split the payment" / "two payments" → Split payment
- "milestone-based" / "stage-based" → Stage billing
- "installments" → Discuss structure

### 13.5 Net Payment Day Signals

- Default (no signal): 30 days
- "net 45" / "45 days" / "forty-five days" → 45-day terms (requires CFO approval)
- "net 30" / "30 days" → 30-day terms (confirming default)
- "net 60" / "60 days" → 60-day terms (flag for approval)

### 13.6 Chemistry Call Status Signals

- "chemistry meeting is done" / "chemistry call completed" / "already met the coach"
- "coach has been selected" / "[coach name] will be their coach"
- "introduced to [coach name]" / "they met with [coach name]"
- Any confirmation that a specific coach has been assigned

If none of these: assume chemistry call has NOT been completed. Use placeholder.

### 13.7 Tier Selection Signals

| Signal | Maps To |
|--------|---------|
| "C-Suite" / "CEO" / "COO" / "CFO" / "President" | ASCENT |
| "executive advisory" / "on-demand" / "advisory coaching" | AIIR VISTA |
| "senior leader" / "VP" / "Director" + "nine months" | IGNITE |
| "six months" / "6-month" alone → check seniority | IGNITE (senior) or ROADMAP (mid) |
| "manager" / "mid-level" / "team lead" + "four to six months" | ROADMAP |
| "early career" / "new manager" / "three to four months" | SPARK I |
| "early career" / "new manager" / "four to five months" | SPARK II |

---

## 14. Known Errors & Corrections in Source Files

The source Excel file and SOW template contain several errors or discrepancies that were discovered during the audit of Andrew's comments and Megan's Zoom transcript. All of these must be handled correctly by the AI agent.

### Confirmed Corrections (from Audit)

| # | Issue | Wrong Value in File | Correct Value | Source |
|---|-------|---------------------|---------------|--------|
| 1 | **Margin (B16)** | 0.70 (70%) | **0.65 (65%)** | Andrew's comment on B16: *"Megan's zoom, she has 65% (not 70%), and she said this is very standard"* |
| 2 | **CZ Rate for IGNITE (F37)** | Was $50 previously | **$75 (current correct value)** | Andrew's comment on F37: *"per Megan zoom, this is now $75 (not $50)"* |
| 3 | **Payment default** | Shown as 50/50 in template SOW | **100% upfront is the default** | Andrew's comment on the payment section: *"The default is actually 100% upon kickoff"* |
| 4 | **Dev Planning Session minimum** | Listed as lever alongside stakeholder sessions | **Min = 0 hrs (fully removable)** | Andrew's comment C42: *"In severe cases, I might remove this"* |
| 5 | **CZ months for IGNITE** | Treated as fixed 9 months | **Variable: 7–9 months** | Andrew's comment on E37 referencing Megan's statement |
| 6 | **ASCENT and VISTA CZ rate** | Same as other tiers assumed | **$50/month** (F55 and F107) | Excel data: F55 = 50.0, F107 = 50.0 |
| 7 | **IGNITE LD12 360° inclusion** | Sometimes assumed included | **Not included (E38 = 0)** | Excel data: IGNITE E38 = 0 |
| 8 | **ROADMAP LD12 360° inclusion** | Sometimes assumed excluded | **Included (E22 = 1)** | Excel data: ROADMAP E22 = 1 |
| 9 | **SPARK I Dev History** | Assumed to be a coaching session | **No interview. Uses $60 survey (E77)** | Excel data: SPARK I has no B-column Dev History row |
| 10 | **Assessment Feedback SOW rule** | Assumed: if unchanged, keep text | **If 2 hrs (default): delete duration sentence** | Andrew's comment 9 |
| 11 | **360° minimum** | Sometimes stated as "5-6" | **Hard floor: exactly 5 interviews** | Megan's exact words: *"I'm not gonna go lower than 5"* |
| 12 | **"Client A" replacement count** | Assumed 1 instance | **3 separate instances** in document | Andrew's comments 14, 15, 16 |

---

## 15. Data Extraction Specification — What to Pull From a Transcript

This section specifies exactly what the AI must extract from a client meeting transcript to fully populate the SOW. This is the complete variable list.

### 15.1 Required Variables

| Variable | Extraction Method | Where Used |
|----------|------------------|------------|
| **client_company_name** | NLP entity extraction. The company that is buying the coaching engagement (the sponsor). | SOW: 3 locations (body ×2, signature block) |
| **coachee_name** | NLP entity extraction. The individual being coached. | SOW: greeting, program header |
| **hubspot_deal_id** | Look for "deal ID", "opportunity ID", reference numbers, or any ID format mentioned | SOW: header + footer |
| **coach_name** | Only if chemistry call confirmed. Look for AIIR coach name mentioned. | SOW: program description paragraph |
| **seniority_level** | Title detection + context (C-Suite, VP, Director, Manager, etc.) | Tier selection + bill rate |
| **market_type** | Country/region detection | Bill rate |
| **engagement_duration_months** | Any mention of program duration | Tier selection + CZ months |
| **num_participants** | How many people are being enrolled | Excel E49 + total price |
| **budget_signals** | Any cost constraint language | Reduction hierarchy trigger |
| **budget_target_amount** | If a specific dollar figure is mentioned as a limit | Reduction stopping point |
| **existing_360_status** | Has a 360 been completed recently? | 360° eliminate decision |
| **self_awareness_signals** | Any of the 360° keep signal keywords | 360° keep decision |
| **payment_structure_signal** | Any payment schedule discussion | Payment terms |
| **net_days_signal** | Any mention of payment terms / net days | Net days |
| **coachee_terminology** | Does sponsor say "client" or "coachee"? | SOW terminology |
| **chemistry_call_complete** | Confirmation that chemistry call has occurred | Coach name decision |

### 15.2 Output Variables (Calculated, Not Extracted)

| Variable | Calculated How | Where Used |
|----------|---------------|------------|
| **selected_tier** | Tier selection logic in Step 4 | Determines Excel section |
| **bill_rate** | Market type + seniority lookup | Excel B15 |
| **cz_months** | Extracted duration + tier range | Excel E37 (or equivalent) |
| **reduced_session_hours** | Reduction hierarchy results | Excel session cells |
| **price_per_participant** | Excel H48 (after all writes) | SOW price field |
| **total_engagement_price** | Excel H50 (= H48 × E49) | SOW price field |
| **payment_structure** | Payment detection logic | SOW payment section |
| **net_days** | Net day detection logic | SOW payment section |

---

## 16. Human Review Checkpoints

There are exactly 2 mandatory human review checkpoints before the SOW is sent to a client.

### Checkpoint 1: Pricing Review

**What the human receives:**
1. The filled-in Excel pricing calculator (pre-populated with AI-determined values)
2. A pricing rationale document explaining every decision:
   - Which tier was selected and why
   - What bill rate was set and why
   - Whether budget constraints were detected (and which keywords)
   - Each reduction lever applied (what changed, before/after values, price impact)
   - 360° decision (kept/reduced/eliminated and reasoning)
   - Payment terms applied

**Human actions:**
- **Approve:** Explicitly confirm pricing is correct (via status cell, comment, or file move)
- **Adjust:** Modify any cell manually, then approve

**Gate:** SOW generation CANNOT begin until this checkpoint is explicitly passed.

---

### Checkpoint 2: SOW Review

**What the human receives:**
1. A fully populated SOW Word document (all variables injected, all conditional text updated)

**Human actions:**
- **Approve:** Trigger send to client
- **Edit:** Make changes in Google Docs or Word, then approve

**Gate:** SOW cannot be sent until this checkpoint is explicitly passed.

---

## 17. Archiving & CRM Update Logic

After the SOW is approved and sent:

### File Naming Convention

```
[ClientCompanyName]_[CoacheeName]_[Tier]_SOW_[YYYY-MM-DD].docx
```

Example: `AcmeCorp_JohnSmith_IGNITE_SOW_2026-03-10.docx`

### Google Drive Archiving

1. Save the final SOW to the client's folder: `/Client Master Folder/[ClientCompanyName]/SOWs/`
2. Save the approved pricing Excel: `/Client Master Folder/[ClientCompanyName]/Pricing/`
3. Save the transcript: `/Client Master Folder/[ClientCompanyName]/Transcripts/`

### HubSpot Update

Update the deal record:
- Status → "SOW Sent"
- SOW file → attach or link
- SOW sent date → today's date
- Deal amount → value from H50

---

## 18. Implementation Notes & Constraints

### Technology Stack (Recommended)

The system will likely be built using:
- **Google Drive** — for trigger (file upload) and archiving
- **Make.com or Zapier** — for workflow automation
- **Anthropic Claude API** — for transcript parsing and NLP extraction
- **Python or JavaScript** — for Excel read/write (using openpyxl for Python or exceljs for Node)
- **Google Docs API or python-docx** — for SOW Word template manipulation
- **HubSpot API** — for deal status updates

### Excel Read/Write Notes

- The Excel file uses `.xlsx` format
- Cell writes must be done programmatically using a library (openpyxl in Python, ExcelJS in Node)
- Excel formulas auto-calculate on save — the AI only needs to write to input cells
- **Do NOT write to auto-calculated cells** (B47, B48, B49, B50, H44, H47, H48, H50 — these are formula cells)
- Always write `E49` (participant count) BEFORE reading H50 (total price), as H50 depends on E49
- The B16 correction (0.65) must be applied every time

### SOW Word Document Notes

- The SOW is a `.docx` file
- Manipulation should use python-docx or direct XML editing
- Andrew's comments are embedded in the document XML — they identify the exact location of each variable field
- **Do NOT remove or alter Andrew's comments** — they serve as field markers for the automation
- When replacing text, use exact string matching for each field's placeholder text

### NLP Processing Notes

- Transcripts may include speaker labels (e.g., "Megan:", "Client:") — strip these for analysis
- Transcripts may be from Fireflies, Otter.ai, Zoom, or manual notes — normalize format
- All keyword matching should be case-insensitive
- For budget amounts, extract numeric values with currency context (e.g., "$15,000", "15K", "fifteen thousand")

### Edge Cases to Handle

| Edge Case | Handling |
|-----------|----------|
| No budget signals found | Use all defaults. No reduction. |
| Budget target found but defaults already below it | No reduction needed. Flag that defaults are within budget. |
| Multiple tiers could apply | Flag for human. Do not auto-select ambiguously. |
| No seniority level detected | Default to IGNITE tier + Tier 1 bill rate + flag for human |
| No participant count found | Default to 1 participant + flag for human |
| SPARK I selected but Dev History interview reduction requested | N/A — SPARK I has no Dev History interview. Skip that lever. |
| All 6 levers applied and price still above budget | Flag for human review. Do not attempt additional reductions beyond defined levers. |
| 360° keep AND eliminate signals both present | KEEP wins. Keep the 360°. |
| Coach name mentioned but chemistry call status unclear | Use placeholder "a Senior Level AIIR Consultant" |

---

## Appendix A: IGNITE SOW Example Values (Client A Reference)

The sample SOW (`Client_A_EC_Jonathan_Bailey.docx`) contains these filled-in values for reference:

- **Client Company:** Client A
- **Coachee:** Jonathan Bailey
- **Coach:** Jonathan Kirschner (post-chemistry call)
- **Tier:** IGNITE
- **Price:** $27,445 (per participant)
- **Payment:** 50% upfront + 50% at month 3 (this was negotiated — NOT the default)
- **Net Terms:** 45 days (this was negotiated — NOT the default)
- **HubSpot ID:** 395830485039589

These values are NOT defaults. They represent one specific negotiated deal. The AI should use this file only as a structural template, not as a source of default values.

---

## Appendix B: Megan's Exact Quotes (Key Business Rules)

These direct quotes from Megan's Zoom recording are the authoritative source for the rules:

> **On stakeholder sessions:** *"Typically, these 4 are about 1 hour long. Could drop the time down to 1/2 hour if needed. That's about as low as I would go, for these stakeholder meetings."*

> **On Dev History Interview:** *"Max, typically, that's 2 hours. I might drop this down to 90 minutes. I try not to go lower than 90 minutes."*

> **On 360° interviews:** *"I can move this down to, let's say, 6. I'm not gonna go, though, lower than 5, typically."*

> **On Assessment Feedback:** *"Assessment feedback session is typically 2 hours. I try not to cut down. The lowest I would go is 90 minutes."*

> **On Development Planning Session:** *"In severe cases, I might remove this, but I tend to always keep it."*

> **On IGNITE duration:** *"We have here it's 7 to 9 months. So what I'm going to do is we have a coaching zone fee."*

> **On the Hogan Insight:** *"The Hogan Insight is actually 3 assessments from Hogan. HPI, HDS, and MBPI."*

> **On total hours:** *"So here you're looking at 23.5 hours of coaching, and that's very, very, very standard for a 9 [month] executive coaching engagement."*

---

## Appendix C: Quick Reference Checklist for Agent

Every time a transcript is processed, the agent must complete all of these steps:

- [ ] Parse and validate transcript
- [ ] Extract all 15 required variables (Section 15.1)
- [ ] Select coaching tier
- [ ] Determine coach name (real vs. placeholder)
- [ ] Set bill rate (B15) — detect market type + seniority
- [ ] Set margin (B16) = 0.65 — override file value
- [ ] Detect budget signals
- [ ] If budget signals: apply reduction hierarchy (levers 1–6 in order)
- [ ] Apply 360° sub-logic
- [ ] Write participant count (E49 or tier equivalent) — FIRST
- [ ] Write all other session hour cells
- [ ] Write CZ months
- [ ] Read calculated price from H50 (or tier equivalent)
- [ ] Detect payment terms
- [ ] Generate pricing rationale document
- [ ] [CHECKPOINT 1: Human reviews pricing]
- [ ] Replace Header/Footer ID (comments 0 and 1)
- [ ] Keep boilerplate paragraph intact (comment 2)
- [ ] Update stakeholder count text if changed (comment 3)
- [ ] Replace coach name (comment 4)
- [ ] Update client/coachee terminology (comment 5)
- [ ] Update Dev History duration in table (comment 6)
- [ ] Update 360° count or remove row (comment 7)
- [ ] Update "three/two streams" text (comment 8)
- [ ] Handle Assessment Feedback duration sentence (comment 9)
- [ ] Update Development Planning duration/row (comment 10)
- [ ] Replace total price (comment 11)
- [ ] Set payment structure (comment 12)
- [ ] Set net payment days (comment 13)
- [ ] Replace "Client A" — instance 1 in policy (comment 14)
- [ ] Replace "Client A" — instance 2 in policy (comment 15)
- [ ] Replace "Client A" in signature block (comment 16)
- [ ] [CHECKPOINT 2: Human reviews SOW]
- [ ] Send SOW to client
- [ ] Archive to Google Drive
- [ ] Update HubSpot

---

*End of document. This specification was compiled from: AIIR Excel Pricing Calculator (cell comments), Client A SOW template (Andrew's 17 comments), Andrew Line's March 6 email to Megan, and Megan Marshall's Zoom walkthrough recording. All business rules are ultimately sourced from Megan Marshall, Managing Partner, AIIR Consulting.*
