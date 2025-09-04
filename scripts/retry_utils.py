#!/usr/bin/env python3
"""
Simple retry utilities with exponential backoff and jitter for Google Drive operations.
"""
import time
import random
import logging
from typing import Callable, Any, Optional

try:
    from googleapiclient.errors import HttpError
except ImportError:
    # HttpError not available if googleapiclient not installed
    class HttpError(Exception):
        def __init__(self, resp, content):
            self.resp = resp
            self.content = content
            super().__init__(f"HTTP {resp.status}: {content}")


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    *args,
    **kwargs
) -> Any:
    """
    Retry a function with exponential backoff and jitter.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        *args, **kwargs: Arguments to pass to the function
    
    Returns:
        Result of the function call
        
    Raises:
        The last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
            
        except HttpError as e:
            last_exception = e
            status_code = e.resp.status if hasattr(e, 'resp') else None
            
            # Don't retry on client errors (4xx) except 429 (rate limit)
            if status_code and 400 <= status_code < 500 and status_code != 429:
                raise
            
            # Don't retry on last attempt
            if attempt >= max_retries:
                break
                
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            
            # Add jitter if enabled
            if jitter:
                jitter_range = delay * 0.25
                delay += random.uniform(-jitter_range, jitter_range)
            
            delay = max(0, delay)
            
            print(f"Retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries + 1}): {e}")
            time.sleep(delay)
            
        except Exception as e:
            last_exception = e
            if attempt >= max_retries:
                break
                
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            if jitter:
                jitter_range = delay * 0.25
                delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)
            
            print(f"Retrying in {delay:.2f}s (attempt {attempt + 1}/{max_retries + 1}): {e}")
            time.sleep(delay)
    
    raise last_exception


def simple_circuit_breaker(func: Callable, failure_threshold: int = 3, *args, **kwargs) -> Any:
    """
    Simple circuit breaker that fails fast after too many failures.
    This is a basic implementation - for production, you'd want state persistence.
    """
    # In a real implementation, you'd store this state somewhere persistent
    # For now, we'll just track failures in a simple way
    if not hasattr(simple_circuit_breaker, '_failure_count'):
        simple_circuit_breaker._failure_count = 0
    
    if simple_circuit_breaker._failure_count >= failure_threshold:
        raise Exception(f"Circuit breaker open - too many failures ({failure_threshold})")
    
    try:
        result = func(*args, **kwargs)
        # Reset failure count on success
        simple_circuit_breaker._failure_count = 0
        return result
    except Exception as e:
        simple_circuit_breaker._failure_count += 1
        raise
