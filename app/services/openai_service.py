"""
OpenAI Service for AI Extraction
Uses GPT-4o with structured outputs to extract variables from transcripts
"""

from typing import Dict, Any
from openai import OpenAI
from app.models import ExtractedVariables
import logging
import json

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    OpenAI service for transcript extraction

    Uses GPT-4o with structured output to extract:
    - Client and coachee information
    - Seniority level and engagement duration
    - 360° signals (40+ keywords)
    - Budget constraints
    - Payment terms
    - Special flags
    """

    def __init__(self, api_key: str):
        """
        Initialize OpenAI service

        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)

    def extract_variables_from_transcript(
        self,
        transcript: str
    ) -> ExtractedVariables:
        """
        Extract structured variables from discovery call transcript

        Args:
            transcript: Raw transcript text

        Returns:
            ExtractedVariables object with all extracted data
        """
        try:
            # Build extraction prompt
            system_prompt = self._build_system_prompt()
            user_prompt = f"""Extract all relevant variables from this discovery call transcript:

{transcript}

Extract all information accurately, including:
1. Client and coachee details
2. Seniority level and engagement duration
3. Self-awareness or performance risk signals (look for exact keywords)
4. Existing 360° status
5. Budget constraints (explicit ceiling or sensitivity phrases)
6. Payment terms mentioned
7. Special flags (TES, MSA, custom template)
"""

            # Call OpenAI with JSON mode (structured output)
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent extraction
            )

            # Parse JSON response into ExtractedVariables model
            json_response = json.loads(response.choices[0].message.content)
            extracted = ExtractedVariables(**json_response)

            logger.info(f"Extracted variables: company={extracted.client_company_name}, "
                       f"coachee={extracted.coachee_name}, signals={len(extracted.self_awareness_signals)}")

            return extracted

        except Exception as e:
            logger.error(f"Error extracting variables from transcript: {e}")
            raise

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with all keywords and logic"""

        return """You are an expert at extracting structured information from executive coaching discovery call transcripts.

Your task is to extract all relevant variables that will be used for pricing and SOW generation.

## Key Extraction Guidelines:

### 1. Seniority Level Classification
- **C-Suite:** CEO, CFO, COO, CRO, CMO, CHRO, CTO, President
- **Senior:** SVP, Senior VP, VP, Vice President
- **Mid-level:** Director, Senior Director
- **Early Career:** Manager, Individual Contributor
- **Advisory:** Explicitly mentioned advisory or board-level engagement

### 2. 360° Assessment Signals

**KEEP Signals (look for these exact phrases):**
- "self-awareness" or "self awareness"
- "leadership brand"
- "executive presence"
- "how others experience them" or "how they are experienced"
- "reputation internally"
- "influence with stakeholders"
- "stakeholder perception"
- "blind spots" or "blind spot"
- "needs honest feedback" or "needs feedback"
- "needs broader perspective" or "broader perspective"
- "performance concerns" or "performance concern"
- "performance issues" or "performance issue"
- "needs to work on stakeholder relationships" or "stakeholder relationships"
- "communication or presence issues" or "communication issues" or "presence issues"
- "feedback from the team hasn't been great" or "team feedback"
- "needs to improve"
- "development opportunity" or "development opportunities"
- "areas for growth" or "areas to improve"

**ELIMINATE Signals (existing 360°):**
- "just completed a 360" or "completed a 360"
- "already completed 360"
- "we already have feedback from the organization" or "already have feedback"
- "they went through a 360" or "went through 360"
- "last quarter" (in context of 360°)
- "we can share their previous assessment" or "previous assessment"
- "recent 360"
- "existing 360"
- "360 was done" or "360 is done"

### 3. Budget Constraint Signals

Look for phrases indicating budget sensitivity:
- "we've only used independent coaches before" or "only used independent coaches"
- "our benchmark is around" or "benchmark is"
- "that price feels high" or "price feels high" or "feels high for coaching"
- "we need something more cost-conscious" or "more cost-conscious" or "cost-conscious"
- "we like your offering, but it's outside our usual range" or "outside our usual range" or "outside our range"
- "typically pay around" or "usually pay"
- "we do not pay over" or "don't pay over" or "do not pay more than"
- "maximum of" or "budget is" or "budget ceiling"

Extract explicit budget ceiling if mentioned (e.g., "$25,000 maximum")

### 4. Payment Terms

Look for mentions of:
- "Net 45" or "45 days" → Net 45 days
- "Net 30" or "30 days" → Net 30 days
- "50/50 split" or "half now half later" or "50 percent upfront" → Split payment
- "quarterly payments" or "installments" or "spread it out" → Installments
- "upon completion" or "when finished" or "after delivery" → Payment after completion

### 5. Special Flags

- **TES (Team Effectiveness):** "team effectiveness", "team dynamics", "group coaching", "team assessment", "leadership team development"
- **MSA Rate Card:** "MSA", "master service agreement", "rate card", "predetermined rates", "contract rate"
- **Custom Template:** "use our template", "client SOW template", "our format", "our contract format", "we have our own template"

## Critical Rules:

1. Extract ALL matching keywords/phrases - don't skip any
2. Be literal with keyword matching - include the actual phrase found
3. If budget ceiling is mentioned with a number, extract it (e.g., "$25,000" → 25000.0)
4. Market type defaults to "Mature" unless clear startup/emerging market indicators
5. If engagement duration is a range (e.g., "6-9 months"), use the midpoint or higher value
6. Extract decision maker email even if different from coachee
7. Include all development opportunities and success criteria mentioned

Return all extracted information as a FLAT JSON object with these exact field names (use snake_case, not nested objects):
- client_company_name (string)
- coachee_name (string)
- coachee_title (string)
- coachee_email (string or null)
- decision_maker_name (string or null)
- decision_maker_email (string)
- decision_maker_title (string or null)
- seniority_level (enum: "C-Suite", "Senior", "Mid-level", "Early Career", "Advisory")
- engagement_duration_months (integer or null)
- market_type (enum: "Mature" or "Emerging")
- client_location_city (string or null)
- client_location_state (string or null)
- client_location_country (string, default "United States")
- deal_id (string or null)
- self_awareness_signals (array of strings)
- existing_360_status (string or null)
- budget_ceiling (number or null)
- budget_constraint_phrases (array of strings)
- payment_terms_phrases (array of strings)
- tes_addon_requested (boolean)
- msa_rate_card_mentioned (boolean)
- custom_template_requested (boolean)
- development_opportunities (array of strings)
- success_criteria (array of strings)
- additional_notes (string or null)

IMPORTANT: Your response must be valid JSON only, no other text. Use exact field names as listed above."""

    def generate_pricing_rationale(
        self,
        extracted: ExtractedVariables,
        pricing_context: Dict[str, Any]
    ) -> str:
        """
        Generate AI-enhanced pricing rationale

        Args:
            extracted: Extracted variables
            pricing_context: Context about pricing decisions made

        Returns:
            Enhanced rationale text
        """
        try:
            prompt = f"""Generate a detailed pricing rationale for this coaching engagement:

**Client:** {extracted.client_company_name}
**Coachee:** {extracted.coachee_name} ({extracted.coachee_title})
**Tier:** {pricing_context.get('tier')}
**Price:** ${pricing_context.get('price'):,.0f}

**Key Decisions Made:**
{json.dumps(pricing_context, indent=2)}

Write a clear, professional rationale explaining why this pricing was selected, referencing:
1. The tier selection based on seniority and duration
2. The 360° decision and why (if kept, reduced, or eliminated)
3. Any budget reductions applied and why
4. Total value proposition for the client

Keep it concise (3-4 paragraphs) and client-facing."""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an executive coaching pricing specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            rationale = response.choices[0].message.content

            logger.info("Generated AI-enhanced pricing rationale")
            return rationale

        except Exception as e:
            logger.error(f"Error generating rationale: {e}")
            raise
