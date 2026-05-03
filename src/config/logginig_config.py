import sys
from loguru import logger
from pathlib import Path
 
def setup_logging(log_level: str = "INFO"):
    """
    Configure application-wide logging using loguru
    """
    
    # Remove default handler
    logger.remove()
    
    # Console handler (colored, formatted)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )
    
    # File handler - general logs
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # New file daily
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Error handler - separate file for errors
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
    )
    
    return logger