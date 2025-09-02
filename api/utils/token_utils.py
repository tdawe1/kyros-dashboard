import os
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuration
MAX_INPUT_CHARACTERS = int(os.getenv("MAX_INPUT_CHARACTERS", "100000"))
MAX_TOKENS_PER_JOB = int(os.getenv("MAX_TOKENS_PER_JOB", "50000"))
TOKEN_ESTIMATION_FACTOR = float(os.getenv("TOKEN_ESTIMATION_FACTOR", "1.3"))

def estimate_tokens(text: str) -> int:
    """
    Estimate token count using simple heuristics.
    
    Args:
        text: Input text to estimate tokens for
    
    Returns:
        int: Estimated token count
    """
    if not text:
        return 0
    
    # Simple word-based estimation
    # Remove extra whitespace and split by whitespace
    words = re.findall(r'\S+', text)
    word_count = len(words)
    
    # Apply estimation factor (tokens ~= words * 1.3)
    estimated_tokens = int(word_count * TOKEN_ESTIMATION_FACTOR)
    
    logger.debug(f"Text length: {len(text)} chars, Words: {word_count}, Estimated tokens: {estimated_tokens}")
    return estimated_tokens

def validate_input_limits(text: str) -> Dict[str, Any]:
    """
    Validate input text against character and token limits.
    
    Args:
        text: Input text to validate
    
    Returns:
        dict: Validation result with status and details
    """
    result = {
        "valid": True,
        "errors": [],
        "stats": {
            "character_count": len(text),
            "estimated_tokens": 0,
            "max_characters": MAX_INPUT_CHARACTERS,
            "max_tokens": MAX_TOKENS_PER_JOB
        }
    }
    
    # Check character limit
    if len(text) > MAX_INPUT_CHARACTERS:
        result["valid"] = False
        result["errors"].append(
            f"Input text exceeds maximum character limit of {MAX_INPUT_CHARACTERS:,}. "
            f"Current length: {len(text):,} characters."
        )
    
    # Estimate tokens
    estimated_tokens = estimate_tokens(text)
    result["stats"]["estimated_tokens"] = estimated_tokens
    
    # Check token limit
    if estimated_tokens > MAX_TOKENS_PER_JOB:
        result["valid"] = False
        result["errors"].append(
            f"Estimated token usage ({estimated_tokens:,}) exceeds maximum limit of {MAX_TOKENS_PER_JOB:,} tokens per job."
        )
    
    return result

def get_token_usage_stats(text: str) -> Dict[str, Any]:
    """
    Get detailed token usage statistics for input text.
    
    Args:
        text: Input text to analyze
    
    Returns:
        dict: Token usage statistics
    """
    words = re.findall(r'\S+', text) if text else []
    word_count = len(words)
    estimated_tokens = estimate_tokens(text)
    
    return {
        "character_count": len(text),
        "word_count": word_count,
        "estimated_tokens": estimated_tokens,
        "estimation_factor": TOKEN_ESTIMATION_FACTOR,
        "limits": {
            "max_characters": MAX_INPUT_CHARACTERS,
            "max_tokens": MAX_TOKENS_PER_JOB
        },
        "usage_percentage": {
            "characters": (len(text) / MAX_INPUT_CHARACTERS) * 100,
            "tokens": (estimated_tokens / MAX_TOKENS_PER_JOB) * 100
        }
    }
