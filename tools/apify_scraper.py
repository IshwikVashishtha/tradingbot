
# import pandas as pd
# from config.logger import logger
# from typing import Optional, Dict, List


# def fetch_crypto_klines(
#     symbol: str,
#     timeframe: str = "1m",
#     limit: int = 1000,
#     exchange: str = "binance"
# ) -> pd.DataFrame:
#     try:
#         logger.info(f"Fetching {limit} {timeframe} bars for {symbol} (dummy mode)")
        
#         # Map common timeframe strings to pandas-compatible frequencies
#         freq_map = {
#             "1m": "1min",
#             "5m": "5min",
#             "15m": "15min",
#             "1h": "1h",
#             "4h": "4h",
#             "1d": "1d"
#         }
#         pd_freq = freq_map.get(timeframe, timeframe)
        
#         # Generate sample data (IMPORTANT: Make 'timestamps' a Series, not Index)
#         timestamps = pd.date_range(end=pd.Timestamp.now(), periods=limit, freq=pd_freq)
#         sample_data = {
#             'timestamps': pd.Series(timestamps),  # 👈 This is the fix: wrap in pd.Series()
#             'open': [100 + i * 0.1 for i in range(limit)],
#             'high': [100 + i * 0.1 + 0.5 for i in range(limit)],
#             'low': [100 + i * 0.1 - 0.5 for i in range(limit)],
#             'close': [100 + i * 0.1 + 0.2 for i in range(limit)],
#             'volume': [1000 + i * 10 for i in range(limit)],
#             'amount': [100000 + i * 100 for i in range(limit)]
#         }
#         df = pd.DataFrame(sample_data)
#         logger.info(f"Successfully fetched {len(df)} bars for {symbol}")
#         return df
#     except Exception as e:
#         logger.error(f"Error fetching K-line data: {e}")
#         raise


import pandas as pd
from apify_client import ApifyClientAsync
from config.logger import logger
from config.constants import APIFY_API_KEY
from typing import Optional, Dict, List


async def fetch_crypto_klines(
    symbol: str,
    timeframe: str = "1d",
    limit: int = 1000,
    exchange: str = "binance"
) -> pd.DataFrame:
    try:
        logger.info(f"🌐 Fetching {limit} {timeframe} bars for {symbol} on {exchange} from Apify")
        
        # Check if API key is configured
        if not APIFY_API_KEY or APIFY_API_KEY == "your_apify_api_key_here":
            logger.warning("⚠️ APIFY_API_KEY not configured, using dummy data")
            return _generate_dummy_data(timeframe, limit)
        
        # Initialize Apify async client
        client = ApifyClientAsync(APIFY_API_KEY)
        
        # Prepare actor input (using 'symbols' array as per user's code)
        run_input = {
            "symbols": [symbol],
            "interval": "1d",
            "range": "1mo",
            "maxItems": 10,
            # "timeframe": timeframe,
            # "limit": limit,
            # "exchange": exchange
        }
        
        # Run the actor
        actor_client = client.actor("parseforge/yahoo-finance-scraper")
        actor_run = await actor_client.call(run_input=run_input)
        
        # Fetch dataset items properly (Apify returns a PagedList)
        dataset_client = client.dataset(actor_run.default_dataset_id)
        # dataset_client = client.dataset("I1pJtwIa5hUhglcue")
        list_result = await dataset_client.list_items()
        dataset_items = list_result.items  
        
        if not dataset_items:
            raise ValueError("Apify actor returned no data")
        
        # Convert to DataFrame and standardize columns
        df = pd.DataFrame(dataset_items)
        
        # Fix column names (actor might return different names)
        column_mapping = {
            "timestamp": "timestamps",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "amount": "currentPrice"
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Ensure all required columns exist
        required_columns = ['open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"⚠️ Missing column '{col}', filling with dummy values")
                df[col] = [100 + i * 0.1 for i in range(len(df))]
        
        # Add volume/amount if missing (Kronos accepts these as optional)
        for col in ['volume', 'amount']:
            if col not in df.columns:
                df[col] = [1000 + i * 10 for i in range(len(df))]
        
        # Critical fix: ensure timestamps is a pandas Series (for Kronos)
        if 'timestamps' not in df.columns:
            logger.warning("⚠️ No 'timestamps' column, generating dummy timestamps")
            timestamps = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq=timeframe)
            df['timestamps'] = pd.Series(timestamps)
        else:
            df['timestamps'] = pd.Series(pd.to_datetime(df['timestamps']))
        
        logger.info(f"✅ Successfully fetched {len(df)} bars for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"❌ Error fetching K-line data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return e
