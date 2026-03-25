"""
360° Interview Decision Logic
Based on Megan Marshall's email (March 6, 2026)

Three decision paths:
1. KEEP (6 hours) - Strong self-awareness or performance risk signals
2. ELIMINATE (0 hours) - Recent 360° already completed
3. REDUCE (3-4 hours) - Budget signal but no strong development needs
"""

from typing import Tuple, List


# Keywords that signal KEEPING the 360° (self-awareness/performance risk)
KEEP_360_KEYWORDS = [
    # Self-awareness signals
    "self-awareness",
    "self awareness",
    "leadership brand",
    "executive presence",
    "how others experience them",
    "how they are experienced",
    "reputation internally",
    "influence with stakeholders",
    "stakeholder perception",
    "blind spots",
    "blind spot",
    "needs honest feedback",
    "needs feedback",
    "needs broader perspective",
    "broader perspective",

    # Performance risk signals (coaching for optimization)
    "performance concerns",
    "performance concern",
    "performance issues",
    "performance issue",
    "needs to work on stakeholder relationships",
    "stakeholder relationships",
    "communication or presence issues",
    "communication issues",
    "presence issues",
    "feedback from the team hasn't been great",
    "team feedback",
    "needs to improve",
    "development opportunity",
    "development opportunities",
    "areas for growth",
    "areas to improve",
]

# Keywords that signal ELIMINATING the 360° (recent completion)
ELIMINATE_360_KEYWORDS = [
    "just completed a 360",
    "completed a 360",
    "already completed 360",
    "we already have feedback from the organization",
    "already have feedback",
    "they went through a 360",
    "went through 360",
    "last quarter",
    "we can share their previous assessment",
    "previous assessment",
    "recent 360",
    "existing 360",
    "360 was done",
    "360 is done",
]


def decide_360_hours(
    self_awareness_signals: List[str],
    existing_360_status: str | None,
    budget_signal_detected: bool,
    tier_default_360_hours: float = 6.0
) -> Tuple[float, str, str]:
    """
    Decide how many hours to allocate for 360° interview process

    Args:
        self_awareness_signals: List of phrases from transcript indicating need for 360°
        existing_360_status: Status of recent 360° if mentioned (e.g., "just completed")
        budget_signal_detected: Whether budget constraint was detected
        tier_default_360_hours: Default 360° hours for the tier (usually 6.0)

    Returns:
        Tuple of (hours, decision, rationale)
        - hours: 0.0 to 6.0 (or tier default)
        - decision: "KEEP", "REDUCE", or "ELIMINATE"
        - rationale: Explanation of the decision

    Logic:
        1. ELIMINATE (0 hours) if recent 360° completed
        2. KEEP (6 hours) if self-awareness signals present
        3. REDUCE (3-4 hours) if budget signal but no self-awareness signals
        4. KEEP by default
    """

    # Path A: ELIMINATE - Recent 360° already completed
    if existing_360_status:
        # Check if any elimination keywords are in the status
        status_lower = existing_360_status.lower()
        for keyword in ELIMINATE_360_KEYWORDS:
            if keyword.lower() in status_lower:
                return (
                    0.0,
                    "ELIMINATE",
                    f"360° eliminated: {existing_360_status}. Will use existing feedback."
                )

    # Path B: KEEP - Self-awareness or performance risk signals present
    if self_awareness_signals and len(self_awareness_signals) > 0:
        signals_str = ", ".join(self_awareness_signals[:3])  # Show first 3
        if len(self_awareness_signals) > 3:
            signals_str += f" (and {len(self_awareness_signals) - 3} more)"

        return (
            tier_default_360_hours,
            "KEEP",
            f"360° kept at {tier_default_360_hours} hours. Signals detected: {signals_str}. "
            "Leader will benefit from deeper qualitative feedback."
        )

    # Path C: REDUCE - Budget signal detected but no strong development needs
    if budget_signal_detected:
        # Reduce from 8 meetings × 45 min (6 hrs) to 6 meetings × 30 min (3 hrs)
        # Or from standard to 4 hours (middle ground)
        reduced_hours = tier_default_360_hours * 0.6  # ~60% of standard

        return (
            reduced_hours,
            "REDUCE",
            f"360° reduced from {tier_default_360_hours} to {reduced_hours} hours due to budget constraints. "
            "No strong self-awareness or performance risk signals detected."
        )

    # Default: KEEP
    return (
        tier_default_360_hours,
        "KEEP",
        f"360° kept at standard {tier_default_360_hours} hours. No elimination or reduction signals detected."
    )


def extract_360_signals_from_text(transcript_text: str) -> List[str]:
    """
    Extract 360° self-awareness and performance risk signals from transcript

    This is a helper function for when we don't have structured AI extraction yet
    In production, OpenAI will extract these signals

    Args:
        transcript_text: Raw transcript text

    Returns:
        List of matching signal phrases
    """
    signals_found = []
    text_lower = transcript_text.lower()

    for keyword in KEEP_360_KEYWORDS:
        if keyword.lower() in text_lower:
            # Find the sentence containing the keyword (rough approximation)
            # In production, AI will extract full context
            signals_found.append(keyword)

    return list(set(signals_found))  # Deduplicate


def check_existing_360_status(transcript_text: str) -> str | None:
    """
    Check if transcript mentions existing/recent 360° completion

    This is a helper function for when we don't have structured AI extraction yet

    Args:
        transcript_text: Raw transcript text

    Returns:
        Status string if found, None otherwise
    """
    text_lower = transcript_text.lower()

    for keyword in ELIMINATE_360_KEYWORDS:
        if keyword.lower() in text_lower:
            # Return the first matching phrase
            return f"Mentioned: '{keyword}'"

    return None
