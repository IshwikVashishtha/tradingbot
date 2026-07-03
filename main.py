import asyncio , random
from config.logger import logger
from agents.data_agent import get_historical_data
from agents.market_agent import find_live_markets
from agents.forecasting_agent import predict_price_movement
from agents.risk_agent import evaluate_trade
from agents.order_agent import execute_trade

async def main():
    logger.info("=" * 60)
    logger.info("🚀 Starting Agentic Trading System")
    logger.info("=" * 60)
    
    try:
        # Step 1: Discover live prediction markets
        logger.info("\n📊 Step 1: Discovering Live Prediction Markets")
        markets_result = await find_live_markets()
        
        if markets_result["status"] != "success" or markets_result["count"] == 0:
            logger.warning("No markets found. Exiting.")
            return
        
        selected_market = markets_result["markets"][0]
        logger.info(f"Selected Market: {selected_market['title']}")
        logger.info(f"Implied Probability: {selected_market['implied_probability']:.2%}")
        
        # Step 2: Fetch historical K-line data (async now!)
        logger.info("\n📈 Step 2: Fetching Historical K-Line Data")
        symbol = f"{selected_market['asset']}-USD"
        data_result = await get_historical_data(symbol, timeframe="1d", limit=1000)
        
        if data_result["status"] != "success":
            logger.error(f"Failed to fetch data: {data_result.get('message')}")
            return
        
        logger.info(f"Fetched {len(data_result['data'])} data points for {symbol}")
        
        # Step 3: Predict price movement
        logger.info("\n🔮 Step 3: Predicting Price Movement")
        prediction_result = predict_price_movement(data_result["data"])
        
        if prediction_result["status"] != "success":
            logger.error(f"Prediction failed: {prediction_result.get('message')}")
            return
        
        predicted_direction = prediction_result["prediction"]
        up_probability = prediction_result["up_probability"]
        logger.info(f"Predicted Direction: {predicted_direction.upper()}")
        logger.info(f"Estimated Up Probability: {up_probability:.2%}")
        
       # Step 4: Evaluate trade with Kelly Criterion
        logger.info("\n⚖️ Step 4: Evaluating Trade with Kelly Criterion")
        risk_result = evaluate_trade(
            true_probability=up_probability,
            implied_probability=selected_market["implied_probability"],
            current_bankroll=10000.0
        )
        
        logger.info(f"Trade Decision: {risk_result['decision'].upper()}")
        if risk_result["decision"] == "TRADE" or risk_result['decision'] == "DO NOT TRADE":
            logger.info(f"Position Size: ${risk_result['position_size']:.2f}")
            logger.info(f"Kelly Fraction: {risk_result['kelly_fraction']:.4f}")
            
            # Step 5: Execute the trade!
            logger.info("\n🛒 Step 5: Executing Trade")
            side = "YES" if predicted_direction == "up" else "NO"
            price = selected_market["implied_probability"] * 100  # Convert probability to cents for prediction markets
            execution_result = await execute_trade(
                market_id=selected_market["market_id"],
                platform=selected_market["platform"],
                asset=selected_market["asset"],
                side=side,
                size=risk_result["position_size"],
                price=price
            )
            
            if execution_result["status"] == "success":
                order = execution_result["order"]
                logger.info(f"📋 Order Summary:")
                logger.info(f"   Order ID: {order['order_id']}")
                logger.info(f"   Side: {order['side']}")
                logger.info(f"   Status: {order['status']}")
                if order["status"] in ["executed", "partial_fill"]:
                    logger.info(f"   Executed Size: ${order['executed_size']:.2f}")
                    logger.info(f"   Avg Fill Price: ${order['avg_fill_price']:.2f}")
            else:
                logger.error(f"Trade execution failed: {execution_result.get('message')}")
        else:
            logger.info(f"Reason: {risk_result['reason']}")
        
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Trading System Execution Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())