
from tools.kelly_criterion import calculate_kelly
from config.logger import logger
from typing import Dict, Any


def evaluate_trade(
    true_probability: float,
    implied_probability: float,
    current_bankroll: float = 10000.0,
    active_exposure: float = 0.0
) -> Dict[str, Any]:
    try:
        logger.info("Risk Agent evaluating trade...")
        result = calculate_kelly(
            true_probability=true_probability,
            implied_probability=implied_probability,
            current_bankroll=current_bankroll,
            active_exposure=active_exposure
        )
        if result["decision"] == "TRADE":
            logger.info(f"Trade approved - Position size: ${result['position_size']:.2f}")
        else:
            logger.info(f"Trade rejected - Reason: {result['reason']}")
        return result
    except Exception as e:
        logger.error(f"Risk Agent error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "decision": "DO NOT TRADE",
            "reason": "Agent error",
            "position_size": 0
        }
