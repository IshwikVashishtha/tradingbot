from config.logger import logger
from typing import Dict, Any
import random
from datetime import datetime


class OrderExecutionEngine:
    """Simulated order execution engine for testing"""
    
    def __init__(self):
        self.pending_orders = []
        self.executed_orders = []
        self.order_counter = 10000  # Start with 5-digit order IDs
    
    def place_order(
        self,
        market_id: str,
        platform: str,
        asset: str,
        side: str,
        size: float,
        price: float
    ) -> Dict[str, Any]:
        """Place a simulated order (FAK/GTD as per project requirements)"""
        try:
            order_id = f"ORD-{self.order_counter}"
            self.order_counter += 1
            
            # Simulate order placement delay
            import asyncio
            # Note: We'll handle async properly in the agent
            # For now, just log the delay
            logger.info(f"📤 Placing {side} order on {platform} for {asset}")
            logger.info(f"💲 Order Size: ${size:.2f}, Price: ${price:.2f}")
            
            # Simulate 90% execution rate
            execution_status = random.choices(
                ["executed", "partial_fill", "rejected"],
                weights=[0.85, 0.10, 0.05]
            )[0]
            
            executed_size = size if execution_status == "executed" else size * 0.5 if execution_status == "partial_fill" else 0.0
            avg_fill_price = price * (1 + random.uniform(-0.002, 0.002))  # Small slippage
            
            order = {
                "order_id": order_id,
                "market_id": market_id,
                "platform": platform,
                "asset": asset,
                "side": side,
                "order_type": "FAK",  # Fill-or-Kill/GTD as per project requirements
                "requested_size": size,
                "executed_size": executed_size,
                "requested_price": price,
                "avg_fill_price": avg_fill_price,
                "status": execution_status,
                "timestamp": datetime.now().isoformat()
            }
            
            if execution_status == "rejected":
                order["reject_reason"] = random.choice(["Insufficient liquidity", "Market moved too fast", "Order too small"])
            
            self.pending_orders.append(order)
            
            if execution_status in ["executed", "partial_fill"]:
                self.executed_orders.append(order)
                # Log trade to both log files and CSV
                log_message = f"[TRADE] {order_id} | {asset} | {side} | Size: ${executed_size:.2f} | Price: ${avg_fill_price:.2f} | Status: {execution_status}"
                logger.bind(TRADE=True).info(log_message)
                logger.info(f"✅ Order {order_id} {execution_status}")
            else:
                logger.warning(f"⚠️ Order {order_id} rejected: {order['reject_reason']}")
            
            return {
                "status": "success",
                "order": order
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to place order: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }


# Global instance
_order_engine = OrderExecutionEngine()


def get_order_engine() -> OrderExecutionEngine:
    return _order_engine