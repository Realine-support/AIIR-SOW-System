"""Business logic modules for AIIR SOW System"""

from .tier_selection import select_tier, get_tier_defaults
from .bill_rate import calculate_bill_rate, estimate_total_cost
from .threesixty_decision import (
    decide_360_hours,
    extract_360_signals_from_text,
    check_existing_360_status,
    KEEP_360_KEYWORDS,
    ELIMINATE_360_KEYWORDS,
)
from .reduction_hierarchy import (
    detect_budget_signal,
    apply_reduction_hierarchy,
    calculate_total_hours,
    estimate_total_price,
    generate_reduction_summary,
    BUDGET_CONSTRAINT_KEYWORDS,
)
from .pricing_calculator import (
    calculate_pricing,
    generate_pricing_rationale,
)

__all__ = [
    "select_tier",
    "get_tier_defaults",
    "calculate_bill_rate",
    "estimate_total_cost",
    "decide_360_hours",
    "extract_360_signals_from_text",
    "check_existing_360_status",
    "KEEP_360_KEYWORDS",
    "ELIMINATE_360_KEYWORDS",
    "detect_budget_signal",
    "apply_reduction_hierarchy",
    "calculate_total_hours",
    "estimate_total_price",
    "generate_reduction_summary",
    "BUDGET_CONSTRAINT_KEYWORDS",
    "calculate_pricing",
    "generate_pricing_rationale",
]
