"""
Bill rate calculation logic
Maps seniority level × market type to hourly coaching rate
"""

from app.models import SeniorityLevel, MarketType


def calculate_bill_rate(
    seniority_level: SeniorityLevel,
    market_type: MarketType
) -> float:
    """
    Calculate hourly bill rate based on seniority and market type

    Bill Rate Table:
    | Seniority Level | Mature Market | Emerging Market |
    |----------------|---------------|-----------------|
    | C-Suite        | $550/hr       | $495/hr (10% discount) |
    | Senior (VP/SVP)| $500/hr       | $450/hr (10% discount) |
    | Mid-level (Dir)| $400/hr       | $360/hr (10% discount) |
    | Early Career   | $350/hr       | $315/hr (10% discount) |
    | Advisory       | $750/hr       | $675/hr (10% discount) |

    Args:
        seniority_level: Leadership level
        market_type: Mature or Emerging market

    Returns:
        Hourly bill rate in dollars
    """

    rate_table = {
        SeniorityLevel.C_SUITE: {
            MarketType.MATURE: 550.0,
            MarketType.EMERGING: 495.0,  # 10% discount
        },
        SeniorityLevel.SENIOR: {
            MarketType.MATURE: 500.0,
            MarketType.EMERGING: 450.0,  # 10% discount
        },
        SeniorityLevel.MID_LEVEL: {
            MarketType.MATURE: 400.0,
            MarketType.EMERGING: 360.0,  # 10% discount
        },
        SeniorityLevel.EARLY_CAREER: {
            MarketType.MATURE: 350.0,
            MarketType.EMERGING: 315.0,  # 10% discount
        },
        SeniorityLevel.ADVISORY: {
            MarketType.MATURE: 750.0,
            MarketType.EMERGING: 675.0,  # 10% discount
        },
    }

    return rate_table[seniority_level][market_type]


def estimate_total_cost(
    bill_rate: float,
    total_hours: float,
    assessment_fee: float = 0.0
) -> float:
    """
    Estimate total engagement cost

    Args:
        bill_rate: Hourly coaching rate
        total_hours: Total coaching hours
        assessment_fee: Fixed assessment fee (tier-specific)

    Returns:
        Total cost in dollars
    """
    coaching_cost = bill_rate * total_hours
    return coaching_cost + assessment_fee
