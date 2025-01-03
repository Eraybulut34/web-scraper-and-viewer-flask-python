import logging
import random
from functools import wraps
import time
from typing import Callable, Any
from config import Config

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
        logger.addHandler(handler)
    
    return logger

def retry(max_attempts: int = 3, delay: int = 2) -> Callable:
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = setup_logger(func.__name__)
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait = delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}")
                    logger.info(f"Retrying in {wait} seconds...")
                    time.sleep(wait)
            
            logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator

def get_random_user_agent() -> str:
    """Return a random user agent from the config."""
    return random.choice(Config.USER_AGENTS)

def sanitize_text(text: str) -> str:
    """Clean and sanitize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove unwanted characters
    text = text.replace("\t", " ").replace("\r", "").replace("\n", " ")
    
    return text.strip()

def format_date(date_str: str, input_format: str = "%Y-%m-%d %H:%M:%S", 
               output_format: str = "%d.%m.%Y %H:%M") -> str:
    """Format date string to desired format."""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to specified length while preserving whole words."""
    if len(text) <= max_length:
        return text
        
    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]
    
    return truncated.rstrip() + suffix 