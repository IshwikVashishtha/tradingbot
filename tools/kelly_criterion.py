
from config.logger import logger
from config.constants import KELLY_FRACTION, MAX_EXPOSURE
from typing import Dict, Any


def calculate_kelly(
    true_probability: float,
    implied_probability: float,
    current_bankroll: float = 10000.0,
    active_exposure: float = 0.0
) -> Dict[str, Any]:
    try:
        logger.info(f"Calculating Kelly criterion - True p: {true_probability:.2%}, Implied p: {implied_probability:.2%}")
        if not 0 <= true_probability <= 1:
            raise ValueError("True probability must be between 0 and 1")
        if not 0 < implied_probability < 1:
            raise ValueError("Implied probability must be between 0 and 1")
        b = (1 - implied_probability) / implied_probability
        q = 1 - true_probability
        kelly_f = (b * true_probability - q) / b
        fractional_kelly = kelly_f * KELLY_FRACTION
        position_size = fractional_kelly * current_bankroll
        max_allowed_exposure = current_bankroll * MAX_EXPOSURE
        new_exposure = active_exposure + position_size
        if kelly_f <= 0:
            decision = "DO NOT TRADE"
            reason = "Negative or zero Kelly fraction - no edge"
            position_size = 0
        elif new_exposure > max_allowed_exposure:
            decision = "DO NOT TRADE"
            reason = f"Exceeds maximum allowed exposure ({MAX_EXPOSURE:.0%})"
            position_size = 0
        elif position_size <= 0:
            decision = "DO NOT TRADE"
            reason = "Position size too small"
            position_size = 0
        else:
            decision = "TRADE"
            reason = "Positive edge and within exposure limits"
        result = {
            "status": "success",
            "decision": decision,
            "reason": reason,
            "true_probability": true_probability,
            "implied_probability": implied_probability,
            "kelly_fraction": kelly_f,
            "fractional_kelly": fractional_kelly,
            "position_size": position_size,
            "current_bankroll": current_bankroll,
            "active_exposure": active_exposure,
            "max_allowed_exposure": max_allowed_exposure
        }
        logger.info(f"Kelly calculation complete - Decision: {decision}")
        return result
    except Exception as e:
        logger.error(f"Error calculating Kelly criterion: {e}")
        return {
            "status": "error",
            "message": str(e),
            "decision": "DO NOT TRADE",
            "reason": "Calculation error",
            "position_size": 0
        }
