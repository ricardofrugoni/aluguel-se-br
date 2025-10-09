"""
Logging configuration for the rental price prediction project.
"""

import logging
import logging.config
from pathlib import Path
from config import PROJECT_ROOT, LOGGING_CONFIG

# Create logs directory
logs_dir = PROJECT_ROOT / "logs"
logs_dir.mkdir(exist_ok=True)

# Update file path in logging config
LOGGING_CONFIG['handlers']['file']['filename'] = str(logs_dir / "rental_prediction.log")

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

# Create logger
logger = logging.getLogger(__name__)

def setup_logging(level=logging.INFO):
    """
    Set up logging for the project.
    
    Args:
        level: Logging level (default: INFO)
    """
    # Set root logger level
    logging.getLogger().setLevel(level)
    
    # Log the setup
    logger.info("Logging configured successfully")
    logger.info(f"Log level: {logging.getLevelName(level)}")
    logger.info(f"Log file: {LOGGING_CONFIG['handlers']['file']['filename']}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

if __name__ == "__main__":
    # Test logging configuration
    setup_logging()
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("Logging configuration test completed. Check logs/rental_prediction.log")
