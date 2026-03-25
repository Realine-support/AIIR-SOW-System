# AIIR SOW System - Complete Business Logic Analysis

**Document Date:** March 12, 2026
**Source:** Email thread analysis + n8n workflow review
**Purpose:** Comprehensive requirements for Python implementation

---

## Table of Contents
1. [Core Business Logic (From n8n)](#core-business-logic-from-n8n)
2. [Enhanced Logic from Email Threads](#enhanced-logic-from-email-threads)
3. [Keyword Extraction Requirements](#keyword-extraction-requirements)
4. [Implementation Priority](#implementation-priority)

---

## Core Business Logic (From n8n)

### 1. Tier Selection Logic

**Input Variables:**
- `seniority_level`: VP / C-Suite / Advisory / etc.
- `engagement_duration_months`: integer
- `advisory_flag`: boolean

**Logic:**
```
IF advisory_flag == true:
    tier = "AIIR_VISTA"

ELSE IF seniority_level == "C-Suite":
    IF engagement_duration_months >= 10:
        tier = "ASCENT"
    ELSE IF 6 <= engagement_duration_months <= 9:
        tier = "ASCENT"
        flags.append("TIER_AMBIGUOUS_DURATION")
    ELSE:
        tier = "ROADMAP"

ELSE IF seniority_level == "Senior" (e.g., VP, SVP):
    IF 6 <= engagement_duration_months <= 9:
        tier = "IGNITE"
    ELSE IF engagement_duration_months >= 10:
        tier = "ASCENT"
    ELSE:
        tier = "ROADMAP"

ELSE IF seniority_level == "Mid-level" (e.g., Director):
    IF 4 <= engagement_duration_months <= 6:
        tier = "ROADMAP"
    ELSE:
        tier = "SPARK_II"

ELSE IF seniority_level == "Early Career":
    IF 4 <= engagement_duration_months <= 5:
        tier = "SPARK_II"
    ELSE IF 3 <= engagement_duration_months <= 4:
        tier = "SPARK_I"
    ELSE:
        tier = "SPARK_I"
```

**Tier Default Hours (Before Reductions):**

| Tier | Impl Sessions | Stakeholder | Dev History | 360° | Assessment Feedback | CZ Range |
|------|--------------|-------------|-------------|------|-------------------|----------|
| IGNITE | 8 | 1 hr | 2 hr | 6 hr (8×45min) | 2 hr | 5-7 months |
| ROADMAP | 5 | 1 hr | 2 hr | 6 hr | 2 hr | 4-6 months |
| ASCENT | 12 | 1 hr | 2 hr | 6 hr | 2 hr | 8-12 months |
| SPARK_I | 3 | 0.5 hr | 1.5 hr | 4 hr | 1.5 hr | 3-4 months |
| SPARK_II | 5 | 1 hr | 2 hr | 5 hr | 2 hr | 4-5 months |
| AIIR_VISTA | Custom | Custom | Custom | Custom | Custom | Advisory |

---

### 2. Bill Rate Calculation

**Input Variables:**
- `market_type`: Mature / Emerging
- `seniority_level`: C-Suite / Senior / Mid-level / Early Career

**Bill Rate Table:**

| Seniority Level | Mature Market | Emerging Market |
|----------------|---------------|-----------------|
| C-Suite | $600/hr | $500/hr |
| Senior (VP/SVP) | $500/hr | $400/hr |
| Mid-level (Director) | $400/hr | $350/hr |
| Early Career | $350/hr | $300/hr |

---

## Enhanced Logic from Email Threads

### 3. 360° Interview Decision Logic (Enhanced)

**Source:** Megan Marshall email, March 6, 2026

**Three Decision Paths:**

#### Path A: KEEP 360° (Standard 6 hours)
**Trigger:** Transcript contains ANY of these keywords/phrases:

✅ **Self-Awareness Signals:**
- "self-awareness"
- "leadership brand"
- "executive presence"
- "how others experience them"
- "reputation internally"
- "influence with stakeholders"
- "stakeholder perception"
- "blind spots"
- "needs honest feedback"
- "needs broader perspective"

✅ **Performance Risk Signals (Coaching for Optimization):**
- "some performance concerns"
- "needs to work on stakeholder relationships"
- "communication or presence issues"
- "feedback from the team hasn't been great"
- "needs to improve"
- "development opportunity"

**Action:** Keep 360° at 8 meetings × 45 minutes = **6 hours**

---

#### Path B: ELIMINATE 360° (0 hours)
**Trigger:** Transcript contains ANY of these phrases:

❌ **Recent 360° Completed:**
- "just completed a 360"
- "we already have feedback from the organization"
- "they went through a 360 last quarter"
- "we can share their previous assessment"
- "recent 360"
- "existing 360" + "recent" or "completed"

**Action:** Set 360° to **0 hours**, use existing feedback

---

#### Path C: REDUCE 360° (5 hours or fewer interviews)
**Trigger:** Budget signal detected AND no self-awareness signals

**Action:** Reduce to 6 meetings × 30 minutes = **3 hours** OR reduce to 5 interviews × 45 minutes = **3.75 hours**

---

### 4. Budget Reduction Hierarchy (Megan's 6-Lever System)

**Source:** Megan Marshall email, March 4, 2026

**Trigger:** Client budget is lower than standard program cost

**Budget Constraint Detection - Keywords:**
- "we've only used independent coaches before"
- "our benchmark is around $X"
- "that price feels high for coaching"
- "we need something more cost-conscious"
- "we like your offering, but it's outside our usual range"
- "typically pay around $X for a X-month coaching engagement"
- "we do not pay over $X for coaching engagements"
- Explicit budget ceiling: "$25,000 max", "under $30k", "budget is $45k"

**Reduction Order (Apply sequentially):**

#### Lever 1: Stakeholder Sessions
- **Standard:** 1 hour (60 minutes)
- **Reduced:** 0.75 hour (45 minutes)
- **Savings:** ~$150-300 depending on bill rate

#### Lever 2: Developmental History Interview
- **Standard:** 2 hours
- **Reduced:** 1.5 hours
- **Savings:** ~$200-300

#### Lever 3: 360° Interview Meetings
- **Standard:** 8 meetings × 45 minutes = 6 hours
- **Option A:** 8 meetings × 30 minutes = 4 hours
- **Option B:** 6 meetings × 45 minutes = 4.5 hours
- **IMPORTANT:** Only reduce if coachee doesn't have strong development needs
- **Check for:** "would really benefit from feedback", "development opportunity they need to work on"
- **Savings:** ~$600-1,200

#### Lever 4: Implementation Sessions
- **Standard:** Varies by tier (8 for IGNITE, 12 for ASCENT, 5 for ROADMAP)
- **Reduced:** Subtract 1 session
- **Example:** IGNITE 8 → 7 sessions
- **Savings:** ~$400-600 per session removed

#### Lever 5: Dev Planning (if applicable)
- **Standard:** 2 hours (some tiers)
- **Reduced:** Remove entirely if budget < $35k
- **Savings:** ~$400-600

#### Lever 6: Assessment Feedback Session
- **Standard:** 2 hours
- **Reduced:** 1.5 hours
- **Note:** "Usually one of the last levers we adjust"
- **Savings:** ~$200-300

**Real-World Example:**
- **Client:** Requested Ignite program
- **Standard Price:** $27,800
- **Client Constraint:** "we do not pay over $25,000 for coaching engagements"
- **Target Price:** $24,900
- **Reductions Applied:** Levers 1, 2, 3, 4 applied sequentially until target reached

---

### 5. Payment Terms Detection

**Source:** Email thread + n8n workflow

**Default:** 100% upfront payment, Net 30 days

**Override Keywords:**

| Phrase in Transcript | Payment Terms |
|---------------------|---------------|
| "Net 45", "45 days" | Net 45 days |
| "Net 30", "30 days" | Net 30 days (standard) |
| "50/50 split", "half now half later", "50 percent upfront" | 50% upfront, 50% at midpoint |
| "quarterly payments", "installments", "spread it out" | Split into N installments |
| "upon completion", "when finished", "after delivery" | 100% upon completion (rare) |

**Action:** Extract payment terms and update SOW accordingly

---

### 6. Additional Signals to Flag (Manual Review Required)

#### MSA Rate Card Override
**Keywords:**
- "MSA", "master service agreement"
- "rate card", "predetermined rates"
- "contract rate", "agreed upon rates"

**Action:** Flag for manual review - may need to override standard bill rate with client's MSA rate

#### Custom Client SOW Template
**Keywords:**
- "use our template", "client SOW template"
- "our format", "our contract format"
- "we have our own template"

**Action:** Flag for manual handling - can't automate custom template generation in v1

#### Team Effectiveness (TES) Add-on
**Keywords:**
- "team effectiveness"
- "team dynamics"
- "group coaching"
- "team assessment"
- "leadership team development"

**Action:** Flag for possible TES add-on to Ignite program (manual pricing review)

---

## Keyword Extraction Requirements

### OpenAI Structured Output Schema Updates

**New Fields to Add to Extraction:**

```python
class ExtractedVariables(BaseModel):
    # ... existing fields ...

    # 360° Decision
    self_awareness_signals: List[str] = Field(
        description="List of self-awareness or performance risk phrases found"
    )
    existing_360_status: Optional[str] = Field(
        description="Status of recent 360° (e.g., 'just completed', 'last quarter', 'recent')"
    )

    # Budget Constraints
    budget_ceiling: Optional[float] = Field(
        description="Explicit budget ceiling mentioned (e.g., $25000)"
    )
    budget_constraint_phrases: List[str] = Field(
        description="Phrases indicating budget sensitivity"
    )

    # Payment Terms
    payment_terms_phrases: List[str] = Field(
        description="Phrases about payment structure (e.g., 'Net 45', '50/50 split')"
    )

    # Add-ons and Flags
    tes_addon_requested: bool = Field(
        description="Team effectiveness add-on mentioned"
    )
    msa_rate_card_mentioned: bool = Field(
        description="MSA or rate card mentioned"
    )
    custom_template_requested: bool = Field(
        description="Client wants to use their own SOW template"
    )
```

### AI Extraction Prompt Updates

**Section to Add:**

```
### 360° Assessment Signals
Look for language suggesting the leader needs deeper feedback:
- Self-awareness gaps (keywords: "self-awareness", "blind spots", "executive presence")
- Performance concerns (keywords: "performance concerns", "stakeholder relationships", "feedback issues")
- Recent 360° completion (keywords: "just completed a 360", "already have feedback")

### Budget Constraint Signals
Identify if the client has budget limitations:
- Explicit budget ceiling (e.g., "we don't pay over $25,000")
- Price sensitivity (e.g., "that feels high", "more cost-conscious")
- Benchmark comparisons (e.g., "typically pay $6,000 for coaching")

### Payment Terms
Extract any discussion about payment structure:
- Payment timing (e.g., "Net 45", "30 days")
- Split payments (e.g., "50/50", "half now")
- Installments (e.g., "quarterly", "spread out")

### Special Flags
- Team Effectiveness add-on requested
- MSA rate card mentioned
- Custom SOW template requested
```

---

## Implementation Priority

### Phase 1: Core Infrastructure ✅
- Configuration module
- Google API services
- OpenAI service
- Email service (Gmail API instead of Resend per user request)
- Redis state management

### Phase 2: Enhanced Business Logic 🔥 **CRITICAL**
1. **360° decision logic with all keywords**
2. **Megan's 6-lever budget reduction hierarchy**
3. **Budget constraint detection**
4. **Payment terms extraction**
5. **MSA/TES/Custom template flagging**

### Phase 3: Workflows
1. Transcript → Pricing (with enhanced logic)
2. SOW Generation
3. Send & Archive

### Phase 4: Testing
- Unit tests for each lever
- Integration tests with real transcripts
- Manual UAT with 3 test scripts (AEC, TST, Test Company)

---

## Questions for Future Clarification

1. **TES Add-on Logic:** What are the exact rules for adding Team Effectiveness to Ignite?
2. **MSA Rate Card Lookup:** Should we maintain a lookup table of client MSA rates?
3. **Custom Template Handling:** What percentage of clients use custom templates? Should we support multiple templates?
4. **Reduction Thresholds:** At what price point do we stop applying levers? (e.g., never go below $20k?)

---

## Summary

**Total Decision Points:** 7 major logic systems
**Total Keywords to Extract:** 40+ phrases
**New Data Model Fields:** 7 new fields
**AI Prompt Sections Added:** 4 new sections

**Key Insight from Emails:**
> "The common trigger is simply 'client budget is lower than the standard program cost.' When that happens, we selectively shorten certain sessions." — Megan Marshall

This system must prioritize **budget-driven reductions** over contextual adjustments, applying Megan's 6-lever hierarchy in exact order.
