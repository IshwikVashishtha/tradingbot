
from loguru import logger
import sys
from pathlib import Path


def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "Megatron_trading_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG"
    )
    logger.add(
        log_dir / "trades_{time:YYYY-MM-DD}.csv",
        format="{time:YYYY-MM-DD HH:mm:ss},{level},{message}",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        filter=lambda record: "TRADE" in record["extra"]
    )
    return logger


logger = setup_logger()
