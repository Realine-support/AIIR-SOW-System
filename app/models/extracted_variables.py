"""
Data models for extracted variables from discovery call transcripts
Enhanced with logic from email thread analysis (Megan Marshall, March 2026)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SeniorityLevel(str, Enum):
    """Leadership seniority levels"""
    C_SUITE = "C-Suite"
    SENIOR = "Senior"  # VP, SVP
    MID_LEVEL = "Mid-level"  # Director
    EARLY_CAREER = "Early Career"
    ADVISORY = "Advisory"


class MarketType(str, Enum):
    """Market maturity classification"""
    MATURE = "Mature"
    EMERGING = "Emerging"


class ProgramTier(str, Enum):
    """AIIR program tiers"""
    IGNITE = "IGNITE"
    ROADMAP = "ROADMAP"
    ASCENT = "ASCENT"
    SPARK_I = "SPARK_I"
    SPARK_II = "SPARK_II"
    AIIR_VISTA = "AIIR_VISTA"


class ExtractedVariables(BaseModel):
    """
    Variables extracted from discovery call transcript using AI

    This model is used as the structured output schema for OpenAI GPT-4o
    All fields must be extractable from the transcript or inferable from context
    """

    # === Core Identification ===
    client_company_name: str = Field(
        description="Full name of the client company"
    )
    coachee_name: str = Field(
        description="Full name of the person being coached (the executive)"
    )
    coachee_title: str = Field(
        description="Job title of the coachee (e.g., 'Chief Revenue Officer')"
    )
    coachee_email: Optional[str] = Field(
        default=None,
        description="Email address of the coachee if mentioned"
    )

    # === Decision Making Contact ===
    decision_maker_name: Optional[str] = Field(
        default=None,
        description="Name of person who can approve SOW (often different from coachee)"
    )
    decision_maker_email: str = Field(
        description="Email of the person to send SOW for approval"
    )
    decision_maker_title: Optional[str] = Field(
        default=None,
        description="Title of decision maker (e.g., 'VP of HR')"
    )

    # === Engagement Details ===
    seniority_level: SeniorityLevel = Field(
        description="Leadership level of the coachee"
    )
    engagement_duration_months: Optional[int] = Field(
        default=None,
        description="Desired coaching engagement duration in months"
    )
    market_type: MarketType = Field(
        default=MarketType.MATURE,
        description="Market maturity: Mature (established companies) or Emerging (startups/growth-stage)"
    )

    # === Location ===
    client_location_city: Optional[str] = Field(
        default=None,
        description="City where client is located"
    )
    client_location_state: Optional[str] = Field(
        default=None,
        description="State/province where client is located"
    )
    client_location_country: str = Field(
        default="United States",
        description="Country where client is located"
    )

    # === Deal Tracking ===
    deal_id: Optional[str] = Field(
        default=None,
        description="Internal deal tracking ID if mentioned"
    )

    # === 360° Assessment Decision (Enhanced from Email Thread) ===
    self_awareness_signals: List[str] = Field(
        default_factory=list,
        description="""
        List of phrases indicating the coachee needs 360° feedback.
        Look for: 'self-awareness', 'leadership brand', 'executive presence',
        'how others experience them', 'reputation internally', 'influence with stakeholders',
        'stakeholder perception', 'blind spots', 'needs honest feedback',
        'needs broader perspective', 'performance concerns', 'stakeholder relationships',
        'communication or presence issues', 'feedback from the team hasn't been great'
        """
    )
    existing_360_status: Optional[str] = Field(
        default=None,
        description="""
        Status of recent 360° assessment if mentioned.
        Look for: 'just completed a 360', 'we already have feedback from the organization',
        'they went through a 360 last quarter', 'we can share their previous assessment',
        'recent 360', 'completed 360'
        """
    )

    # === Budget Constraints (Enhanced from Email Thread) ===
    budget_ceiling: Optional[float] = Field(
        default=None,
        description="""
        Explicit budget ceiling or maximum amount client is willing to pay.
        Look for: 'don't pay over $X', 'budget is $X', 'under $X', 'maximum of $X'
        """
    )
    budget_constraint_phrases: List[str] = Field(
        default_factory=list,
        description="""
        Phrases indicating budget sensitivity or constraints.
        Look for: 'only used independent coaches before', 'benchmark is around $X',
        'that price feels high', 'need something more cost-conscious',
        'outside our usual range', 'typically pay $X for coaching'
        """
    )

    # === Payment Terms ===
    payment_terms_phrases: List[str] = Field(
        default_factory=list,
        description="""
        Phrases about payment structure and timing.
        Look for: 'Net 45', 'Net 30', '50/50 split', 'half now half later',
        'quarterly payments', 'installments', 'spread it out', 'upon completion'
        """
    )

    # === Special Flags and Add-ons ===
    tes_addon_requested: bool = Field(
        default=False,
        description="""
        Team Effectiveness (TES) add-on mentioned.
        Look for: 'team effectiveness', 'team dynamics', 'group coaching',
        'team assessment', 'leadership team development'
        """
    )
    msa_rate_card_mentioned: bool = Field(
        default=False,
        description="""
        MSA or predetermined rate card mentioned.
        Look for: 'MSA', 'master service agreement', 'rate card',
        'predetermined rates', 'contract rate', 'agreed upon rates'
        """
    )
    custom_template_requested: bool = Field(
        default=False,
        description="""
        Client wants to use their own SOW template.
        Look for: 'use our template', 'client SOW template', 'our format',
        'our contract format', 'we have our own template'
        """
    )

    # === Additional Context ===
    development_opportunities: List[str] = Field(
        default_factory=list,
        description="Specific development areas or challenges mentioned for the coachee"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="How the client defines success for this engagement"
    )
    additional_notes: Optional[str] = Field(
        default=None,
        description="Any other relevant context not captured in other fields"
    )


class SessionHours(BaseModel):
    """
    Session hours for a coaching engagement
    Used to track both standard and reduced hours
    """
    implementation_sessions: int = Field(
        description="Number of 1-on-1 coaching implementation sessions"
    )
    stakeholder_sessions_hours: float = Field(
        description="Total hours for stakeholder meetings (typically 1 hr or 0.75 hr)"
    )
    developmental_history_hours: float = Field(
        description="Hours for developmental history interview (typically 2 hr or 1.5 hr)"
    )
    threesixty_interview_hours: float = Field(
        description="Total hours for 360° interview meetings (0 to 6 hrs, typically)"
    )
    assessment_feedback_hours: float = Field(
        description="Hours for assessment feedback session (typically 2 hr or 1.5 hr)"
    )
    dev_planning_hours: float = Field(
        default=0.0,
        description="Hours for development planning (0 or 2 hrs, may be removed for budget)"
    )
    coaching_zone_months: int = Field(
        description="Number of months of Coaching Zone access"
    )


class BudgetReduction(BaseModel):
    """
    A single budget reduction applied to the engagement
    Tracks which lever was applied and the impact
    """
    lever_number: int = Field(
        description="Lever number (1-6) from Megan's hierarchy"
    )
    lever_name: str = Field(
        description="Name of the lever (e.g., 'Stakeholder Sessions')"
    )
    original_hours: float = Field(
        description="Original hours before reduction"
    )
    reduced_hours: float = Field(
        description="Reduced hours after lever applied"
    )
    hours_saved: float = Field(
        description="Hours saved by this reduction"
    )
    cost_saved: float = Field(
        description="Approximate cost saved by this reduction"
    )
    rationale: str = Field(
        description="Why this lever was applied"
    )


class CalculatedPricing(BaseModel):
    """
    Complete pricing calculation result
    Includes tier, hours, bill rate, and total price
    """
    # === Tier Selection ===
    tier: ProgramTier = Field(
        description="Selected program tier"
    )
    tier_selection_flags: List[str] = Field(
        default_factory=list,
        description="Flags/warnings about tier selection (e.g., 'TIER_AMBIGUOUS_DURATION')"
    )

    # === Bill Rate ===
    bill_rate_per_hour: float = Field(
        description="Calculated bill rate based on seniority and market type"
    )

    # === Session Hours ===
    session_hours: SessionHours = Field(
        description="All session hours (after any reductions)"
    )

    # === Budget Reductions Applied ===
    budget_reductions: List[BudgetReduction] = Field(
        default_factory=list,
        description="List of budget reduction levers applied (in order)"
    )
    budget_reduction_triggered: bool = Field(
        default=False,
        description="Whether budget reduction logic was triggered"
    )
    budget_reduction_rationale: Optional[str] = Field(
        default=None,
        description="Why budget reductions were applied"
    )

    # === 360° Decision ===
    threesixty_decision: str = Field(
        description="Decision for 360°: KEEP, REDUCE, or ELIMINATE"
    )
    threesixty_rationale: str = Field(
        description="Explanation for 360° decision"
    )

    # === Total Pricing ===
    total_coaching_hours: float = Field(
        description="Sum of all coaching-related hours"
    )
    total_engagement_price: float = Field(
        description="Total price for the engagement"
    )
    price_per_participant: float = Field(
        description="Price per participant (usually same as total for 1 coachee)"
    )

    # === Payment Terms ===
    payment_terms: str = Field(
        default="100% upfront payment, Net 30 days",
        description="Payment terms extracted from transcript or default"
    )


class EngagementRecord(BaseModel):
    """
    Complete engagement record stored in Tracker sheet
    Combines extracted variables and calculated pricing
    """
    engagement_id: str = Field(
        description="Unique engagement ID (format: CLIENTNAME-YYYYMMDD-HHMM)"
    )
    transcript_filename: str = Field(
        description="Original transcript filename"
    )
    transcript_file_id: str = Field(
        description="Google Drive file ID of the transcript"
    )

    # === Extracted Variables ===
    extracted: ExtractedVariables = Field(
        description="Variables extracted from transcript"
    )

    # === Calculated Pricing ===
    pricing: CalculatedPricing = Field(
        description="Calculated pricing and session hours"
    )

    # === Document URLs ===
    rationale_doc_url: Optional[str] = Field(
        default=None,
        description="URL to the pricing rationale Google Doc"
    )
    calculator_sheet_url: Optional[str] = Field(
        default=None,
        description="URL to the calculator sheet with detailed breakdown"
    )
    sow_doc_url: Optional[str] = Field(
        default=None,
        description="URL to the generated SOW document"
    )

    # === Workflow Status ===
    workflow_status: str = Field(
        default="pricing_review",
        description="Current workflow status: pricing_review, sow_generation, sow_approval, completed"
    )
    created_at: str = Field(
        description="Timestamp when engagement was created"
    )
    updated_at: str = Field(
        description="Timestamp when engagement was last updated"
    )
