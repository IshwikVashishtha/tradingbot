from tools.order_execution import get_order_engine
from config.logger import logger
from typing import Dict, Any
import asyncio , random


async def execute_trade(
    market_id: str,
    platform: str,
    asset: str,
    side: str,
    size: float,
    price: float
) -> Dict[str, Any]:
    """Hermes agent to execute trades via simulated order engine"""
    try:
        logger.info("🚀 Order Agent executing trade...")
        # Simulate slight async delay
        await asyncio.sleep(random.uniform(0.2, 0.8))
        engine = get_order_engine()
        result = engine.place_order(market_id, platform, asset, side, size, price)
        return result
    except Exception as e:
        logger.error(f"❌ Order Agent error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e)
        }