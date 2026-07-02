
print("Testing fetch_crypto_klines...")
from tools.apify_scraper import fetch_crypto_klines
import traceback , asyncio
async def test_fetch_crypto_klines():
    try:
        df = await fetch_crypto_klines("ETH-USD")
        print("SUCCESS: Got DataFrame shape:", df.shape)
        print("Columns:", df.columns)
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
asyncio.run(test_fetch_crypto_klines())

print("\nTesting get_historical_data...")
from agents.data_agent import get_historical_data
async def test_get_historical_data():
    try:
        result = await get_historical_data("ETH-USD")
        print("Result:", result)
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()
asyncio.run(test_get_historical_data())
