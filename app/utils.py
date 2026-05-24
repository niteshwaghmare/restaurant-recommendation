import logging
from typing import List
import re
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class TextUtils:
    """Utilities for text processing and cleaning"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Basic sanitization for LLM output
        - Strip whitespace
        - Remove newlines
        - Remove quotes if present
        """
        cleaned = text.strip()
        cleaned = cleaned.replace("\n", "").replace("\r", "")
        cleaned = cleaned.strip('"\'')
        return cleaned
    
    @staticmethod
    def clean_menu_item(item: str) -> str:
        """Clean individual menu item"""
        item = item.strip()
        # Remove numbering if present (e.g., "1. Item" -> "Item")
        item = re.sub(r"^\d+\.\s*", "", item)
        # Remove bullet points
        item = re.sub(r"^[-•*]\s*", "", item)
        # Remove asterisks/bold formatting
        item = item.replace("**", "").replace("*", "")
        return item.strip()
    
    @staticmethod
    def extract_menu_items(text: str, expected_count: int = 15) -> List[str]:
        """
        Extract menu items from LLM output
        Handles various formatting styles
        """
        # Split by common delimiters
        items = []
        
        # Try splitting by newlines first
        lines = text.split("\n")
        
        for line in lines:
            cleaned = TextUtils.clean_menu_item(line)
            if cleaned and len(cleaned) > 2:  # Avoid single characters
                items.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in items:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                unique_items.append(item)
        
        logger.info(f"Extracted {len(unique_items)} menu items from LLM output")
        
        return unique_items[:expected_count]  # Return only expected count


class ValidationUtils:
    """Utilities for validating generated content"""
    
    @staticmethod
    def validate_restaurant_name(name: str) -> bool:
        """Validate restaurant name"""
        if not name or len(name) < 2 or len(name) > 100:
            return False
        # Check for at least one alphabetic character
        if not any(c.isalpha() for c in name):
            return False
        return True
    
    @staticmethod
    def validate_menu_length(menu: List[str], expected: int = 15) -> bool:
        """Validate menu has expected number of items"""
        return len(menu) == expected
    
    @staticmethod
    def validate_menu_items(menu: List[str]) -> bool:
        """Validate all menu items are non-empty strings"""
        if not isinstance(menu, list):
            return False
        return all(isinstance(item, str) and len(item.strip()) > 0 for item in menu)
    
    @staticmethod
    def validate_no_duplicates(menu: List[str]) -> bool:
        """Validate no duplicate menu items"""
        return len(menu) == len(set(item.lower() for item in menu))


class LoggingUtils:
    """Utilities for structured logging"""
    
    @staticmethod
    def log_generation_start(cuisine: str):
        """Log generation start"""
        logger.info(f"Starting restaurant generation for cuisine: {cuisine}")
    
    @staticmethod
    def log_generation_success(cuisine: str, name: str, item_count: int):
        """Log successful generation"""
        logger.info(
            f"Successfully generated restaurant. "
            f"Cuisine: {cuisine}, Name: {name}, Menu Items: {item_count}"
        )
    
    @staticmethod
    def log_generation_error(cuisine: str, error: str):
        """Log generation error"""
        logger.error(f"Failed to generate restaurant for {cuisine}: {error}")


class RateLimitUtils:
    """Utilities for rate limiting"""
    
    def __init__(self, max_requests: int, time_window_seconds: int = 60):
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.requests: List[datetime] = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit"""
        now = datetime.utcnow()
        # Remove old requests outside time window
        self.requests = [
            req_time for req_time in self.requests
            if (now - req_time).total_seconds() < self.time_window_seconds
        ]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window"""
        now = datetime.utcnow()
        self.requests = [
            req_time for req_time in self.requests
            if (now - req_time).total_seconds() < self.time_window_seconds
        ]
        return max(0, self.max_requests - len(self.requests))
