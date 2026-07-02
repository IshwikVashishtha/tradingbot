
# import pandas as pd
# import torch
# from typing import Dict, Any, Optional
# from config.logger import logger
# from config.constants import KRONOS_TOKENIZER, KRONOS_MODEL, MAX_CONTEXT


# class KronosPredictor:
#     def __init__(self, device: Optional[str] = None):
#         try:
#             if device is None:
#                 self.device = "cuda" if torch.cuda.is_available() else "cpu"
#             else:
#                 self.device = device
#             logger.info(f"Initializing Kronos on device: {self.device}")
#             self.tokenizer = None
#             self.model = None
#             logger.info("Kronos predictor initialized (placeholder mode)")
#         except Exception as e:
#             logger.error(f"Error initializing Kronos: {e}")
#             raise
    
#     def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
#         try:
#             df = df.sort_values('timestamps').copy()
#             if len(df) > MAX_CONTEXT:
#                 df = df.tail(MAX_CONTEXT)
#                 logger.info(f"Trimmed data to {len(df)} bars")
#             return df
#         except Exception as e:
#             logger.error(f"Error preprocessing data: {e}")
#             raise
    
#     def predict(self, df: pd.DataFrame, pred_len: int = 1) -> Dict[str, Any]:
#         try:
#             logger.info(f"Starting prediction with {len(df)} data points")
#             processed_df = self.preprocess_data(df)
#             recent_prices = processed_df['close'].tail(10)
#             if len(recent_prices) >= 2:
#                 trend = recent_prices.iloc[-1] - recent_prices.iloc[0]
#                 if trend > 0:
#                     up_probability = 0.55 + min(0.4, abs(trend) / recent_prices.mean())
#                 else:
#                     up_probability = 0.45 - min(0.4, abs(trend) / recent_prices.mean())
#             else:
#                 up_probability = 0.5
#             prediction = {
#                 "status": "success",
#                 "prediction": "up" if up_probability > 0.5 else "down",
#                 "up_probability": up_probability,
#                 "down_probability": 1 - up_probability,
#                 "prediction_steps": pred_len,
#                 "data_points_used": len(processed_df),
#                 "note": "Placeholder prediction - integrate actual Kronos model for real forecasts"
#             }
#             logger.info(f"Prediction complete: {prediction['prediction']} with {prediction['up_probability']:.2%} up probability")
#             return prediction
#         except Exception as e:
#             logger.error(f"Error making prediction: {e}")
#             return {
#                 "status": "error",
#                 "message": str(e)
#             }

# _predictor_instance: Optional[KronosPredictor] = None


# def get_kronos_predictor() -> KronosPredictor:
#     global _predictor_instance
#     if _predictor_instance is None:
#         _predictor_instance = KronosPredictor()
#     return _predictor_instance








# Kronos AI predictor tool for crypto price forecasting (OFFICIAL INTEGRATION)
import pandas as pd
import torch
from typing import Dict, Any, Optional
from config.logger import logger
from config.constants import MAX_CONTEXT
from .model import Kronos, KronosTokenizer, KronosPredictor as OfficialKronosPredictor


class KronosPredictor:
    def __init__(self, device: Optional[str] = None):
        try:
            # Determine device
            if device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device
            
            logger.info(f"Initializing Kronos on device: {self.device}")
            
            # Load tokenizer and model (Hugging Face Hub)
            self.tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
            self.model = Kronos.from_pretrained("NeoQuasar/Kronos-small").to(self.device)
            
            # Initialize OFFICIAL KronosPredictor
            self.predictor = OfficialKronosPredictor(
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                max_context=MAX_CONTEXT  # Kronos-small uses 512
            )
            
            logger.info("✅ Kronos predictor initialized successfully (OFFICIAL MODE)")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Kronos: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Ensure we have the columns Kronos expects
            required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
            available_columns = [col for col in required_columns if col in df.columns]
            
            # Warn if volume/amount are missing
            if 'volume' not in available_columns:
                logger.warning("⚠️ 'volume' column missing, Kronos will still work")
                df['volume'] = 0
            if 'amount' not in available_columns:
                logger.warning("⚠️ 'amount' column missing, Kronos will still work")
                df['amount'] = 0
            
            df = df[required_columns].copy()
            
            # Sort by timestamp
            df = df.sort_values('timestamps').copy()
            
            # Keep only the last MAX_CONTEXT bars
            if len(df) > MAX_CONTEXT:
                df = df.tail(MAX_CONTEXT)
                logger.info(f"Trimmed data to {len(df)} bars (max_context={MAX_CONTEXT})")
            
            return df
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            raise

    def predict(self, df: pd.DataFrame, pred_len: int = 1) -> Dict[str, Any]:
        try:
            logger.info(f"Starting prediction with {len(df)} data points")
            
            # Prepare inputs as per Kronos documentation (ensure Series, not Index)
            x_df = df[['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
            x_timestamp = df['timestamps'].copy()  # Make sure it's a Series
            
            # Generate y_timestamp (pred_len future timestamps)
            freq = pd.infer_freq(x_timestamp) if len(x_timestamp) > 1 else '1min'
            y_timestamp = pd.date_range(
                start=x_timestamp.iloc[-1],
                periods=pred_len + 1,
                freq=freq
            )[1:]
            y_timestamp = pd.Series(y_timestamp)  # 👈 Also make this a Series
            
            # Generate predictions using official KronosPredictor
            pred_df = self.predictor.predict(
                df=x_df,
                x_timestamp=x_timestamp,
                y_timestamp=y_timestamp,
                pred_len=pred_len,
                T=1.0,  # Temperature for sampling
                top_p=0.9,  # Nucleus sampling
                sample_count=5  # Generate 5 paths and average
            )
            
            # Calculate directional probability (simple example using last close)
            last_known_close = x_df['close'].iloc[-1]
            predicted_close = pred_df['close'].iloc[-1]
            up_probability = 0.7 if predicted_close > last_known_close else 0.3
            
            prediction = {
                "status": "success",
                "prediction": "up" if up_probability > 0.5 else "down",
                "up_probability": up_probability,
                "down_probability": 1 - up_probability,
                "prediction_steps": pred_len,
                "data_points_used": min(len(df), MAX_CONTEXT),
                "predicted_close": predicted_close,
                "prediction_data": pred_df.to_dict(orient='records')
            }
            
            logger.info(f"✅ Prediction complete: {prediction['prediction']} with {prediction['up_probability']:.2%} up probability")
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error making prediction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }

# Global predictor instance
_predictor_instance: Optional[KronosPredictor] = None


def get_kronos_predictor() -> KronosPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = KronosPredictor()
    return _predictor_instance


