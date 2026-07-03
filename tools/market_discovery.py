from typing import List, Dict, Any
from config.logger import logger
from config.constants import ASSETS
import random
from datetime import datetime, timedelta


def _generate_random_market(platform: str, asset: str) -> Dict[str, Any]:
    """Generate a single realistic-looking dummy market (no future dates!)"""
    # Generate random title (past/present tense)
    price_target = round(random.uniform(50000 if asset == "BTC" else 3000, 70000 if asset == "BTC" else 4000), 2)
    timeframe = random.choice(["yesterday", "today", "by end of yesterday", "by end of today"])
    titles = [
        f"Did {asset} close above ${price_target} {timeframe}?",
        f"Was {asset} price above ${price_target} {timeframe}?",
        f"Did {asset} end above ${price_target} {timeframe}?"
    ]
    title = random.choice(titles)
    
    # Generate implied probability (0.2 to 0.8, realistic range)
    implied_prob = round(random.uniform(0.2, 0.8), 2)
    
    # Generate end date (ONLY PAST OR PRESENT: 0-7 days AGO)
    days_ago = random.randint(0, 7)  # 0 = today, 7 = 7 days ago
    end_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Generate market ID
    market_id = f"{platform}_{asset.lower()}_{random.randint(1000, 9999)}"
    
    return {
        "market_id": market_id,
        "platform": platform,
        "title": title,
        "asset": asset,
        "description": f"Binary prediction market for {asset} price (resolved or live)",
        "end_date": end_date,
        "yes_price": implied_prob,
        "no_price": round(1 - implied_prob, 2),
        "implied_probability": implied_prob
    }


async def fetch_polymarket_markets() -> List[Dict[str, Any]]:
    try:
        logger.info("🌐 Fetching markets from Polymarket (simulated)")
        # Simulate API delay (0.5 to 1.5 seconds)
        import asyncio
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Generate 2-4 random Polymarket markets
        num_markets = random.randint(2, 4)
        markets = []
        for asset in ASSETS:
            markets.extend([_generate_random_market("polymarket", asset) for _ in range(random.randint(1, num_markets))])
        
        logger.info(f"✅ Found {len(markets)} Polymarket markets")
        return markets
    except Exception as e:
        logger.error(f"❌ Error fetching Polymarket markets: {e}")
        return []


async def fetch_kalshi_markets() -> List[Dict[str, Any]]:
    try:
        logger.info("🌐 Fetching markets from Kalshi (simulated)")
        # Simulate API delay (0.3 to 1.0 seconds)
        import asyncio
        await asyncio.sleep(random.uniform(0.3, 1.0))
        
        # Generate 1-3 random Kalshi markets
        num_markets = random.randint(1, 3)
        markets = []
        for asset in ASSETS:
            markets.extend([_generate_random_market("kalshi", asset) for _ in range(random.randint(1, num_markets))])
        
        logger.info(f"✅ Found {len(markets)} Kalshi markets")
        return markets
    except Exception as e:
        logger.error(f"❌ Error fetching Kalshi markets: {e}")
        return []


async def discover_markets() -> List[Dict[str, Any]]:
    logger.info("🚀 Starting market discovery...")
    # Fetch markets concurrently (simulates parallel API calls)
    import asyncio
    polymarket_task = fetch_polymarket_markets()
    kalshi_task = fetch_kalshi_markets()
    polymarket_markets, kalshi_markets = await asyncio.gather(
        polymarket_task,
        kalshi_task,
        return_exceptions=True
    )
    
    all_markets = []
    if isinstance(polymarket_markets, list):
        all_markets.extend(polymarket_markets)
    if isinstance(kalshi_markets, list):
        all_markets.extend(kalshi_markets)
    
    # Shuffle markets to mix platforms
    random.shuffle(all_markets)
    
    logger.info(f"🎉 Total markets discovered: {len(all_markets)}")
    return all_markets





# import httpx
# import asyncio
# from typing import List, Dict, Any, Optional
# from config.logger import logger
# from config.constants import ASSETS, POLYMARKET_API_KEY, KALSHI_API_KEY


# async def fetch_polymarket_markets() -> List[Dict[str, Any]]:
#     try:
#         logger.info("🌐 Fetching markets from Polymarket")
#         headers = {
#             "Authorization": f"Bearer {POLYMARKET_API_KEY}"  # Polymarket uses Bearer tokens
#         }
        
#         async with httpx.AsyncClient(timeout=30) as client:
#             response = await client.get(
#                 "https://gamma-api.polymarket.com/markets",
#                 params={"limit": 100, "active": "true"},
#                 headers=headers
#             )
#             response.raise_for_status()
#             markets = response.json()
        
#         filtered_markets = []
#         for market in markets:
#             title = market.get("title", "").lower()
#             for asset in ASSETS:
#                 if asset.lower() in title:
#                     yes_price = market.get("yes_ask", 0)
#                     filtered_markets.append({
#                         "market_id": str(market.get("id")),
#                         "platform": "polymarket",
#                         "title": market.get("title"),
#                         "asset": asset,
#                         "description": market.get("description"),
#                         "end_date": market.get("end_date"),
#                         "yes_price": yes_price,
#                         "no_price": 1 - yes_price if yes_price else 0,
#                         "implied_probability": yes_price
#                     })
#                     break
        
#         logger.info(f"✅ Found {len(filtered_markets)} relevant markets on Polymarket")
#         return filtered_markets
        
#     except Exception as e:
#         logger.error(f"❌ Error fetching Polymarket markets: {e}")
#         return []


# async def fetch_kalshi_markets() -> List[Dict[str, Any]]:
#     try:
#         logger.info("🌐 Fetching markets from Kalshi")
#         headers = {
#             "Authorization": f"Bearer {KALSHI_API_KEY}"  # Kalshi uses Bearer tokens
#         }
        
#         async with httpx.AsyncClient(timeout=30) as client:
#             response = await client.get(
#                 "https://api.kalshi.com/v2/markets",
#                 params={"limit": 100, "status": "active"},
#                 headers=headers
#             )
#             response.raise_for_status()
#             markets_data = response.json()
        
#         filtered_markets = []
#         markets = markets_data.get("markets", [])
#         for market in markets:
#             title = market.get("title", "").lower()
#             for asset in ASSETS:
#                 if asset.lower() in title:
#                     yes_ask = market.get("yes_ask", 0)
#                     filtered_markets.append({
#                         "market_id": str(market.get("id")),
#                         "platform": "kalshi",
#                         "title": market.get("title"),
#                         "asset": asset,
#                         "description": market.get("subtitle"),
#                         "end_date": market.get("close_time"),
#                         "yes_price": yes_ask,
#                         "no_price": 1 - yes_ask if yes_ask else 0,
#                         "implied_probability": yes_ask
#                     })
#                     break
        
#         logger.info(f"✅ Found {len(filtered_markets)} relevant markets on Kalshi")
#         return filtered_markets
        
#     except Exception as e:
#         logger.error(f"❌ Error fetching Kalshi markets: {e}")
#         return []


# ... keep the rest of the file as is (discover_markets and discover_markets_sync)











