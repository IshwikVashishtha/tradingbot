from tools.market_discovery import discover_markets
from config.logger import logger
from typing import Dict, Any, List
import traceback


async def find_live_markets() -> Dict[str, Any]:
    try:
        logger.info("Market Agent discovering live markets...")
        markets = await discover_markets()  
        return {
            "status": "success",
            "count": len(markets),
            "markets": markets
        }
    except Exception as e:
        logger.error(f"Market Agent error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e),
            "count": 0,
            "markets": []
        }