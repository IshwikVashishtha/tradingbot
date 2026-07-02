
import os
from dotenv import load_dotenv

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
MAX_CONTEXT = int(os.getenv("MAX_CONTEXT", "512"))
KRONOS_TOKENIZER = "NeoQuasar/Kronos-Tokenizer-base"
KRONOS_MODEL = "NeoQuasar/Kronos-small"
KELLY_FRACTION = float(os.getenv("KELLY_FRACTION", "0.25"))
MAX_EXPOSURE = float(os.getenv("MAX_EXPOSURE", "0.30"))
ASSETS = ["BTC", "ETH"]
# Polymarket & Kalshi
POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY", "")
KALSHI_API_KEY = os.getenv("KALSHI_API_KEY", "")
