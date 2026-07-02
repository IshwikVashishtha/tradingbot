
import pandas as pd
from tools.kronos_predictor import get_kronos_predictor
from config.logger import logger
from typing import Dict, Any, List


def predict_price_movement(
    kline_data: List[Dict[str, Any]],
    pred_len: int = 1
) -> Dict[str, Any]:
    try:
        logger.info("Forecasting Agent predicting price movement...")
        df = pd.DataFrame(kline_data)
        predictor = get_kronos_predictor()
        prediction = predictor.predict(df, pred_len)
        return prediction
    except Exception as e:
        logger.error(f"Forecasting Agent error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
