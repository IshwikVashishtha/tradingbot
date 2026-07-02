
from tools.apify_scraper import fetch_crypto_klines
from config.logger import logger
from typing import Dict, Any
import traceback


from tools.apify_scraper import fetch_crypto_klines
from config.logger import logger
from typing import Dict, Any
import traceback


async def get_historical_data(
    symbol: str,
    timeframe: str = "1d",
    limit: int = 1000,
    exchange: str = "binance"
) -> Dict[str, Any]:
    try:
        logger.info(f"Data Agent fetching data for {symbol}")
        df = await fetch_crypto_klines(symbol, timeframe, limit, exchange)  
        data_dict = df.to_dict(orient='records')
        logger.info(f"Data Agent returning {len(data_dict)} points")
        return {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "limit": limit,
            "data": data_dict
        }
    except Exception as e:
        logger.error(f"Data Agent error: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e)
        }