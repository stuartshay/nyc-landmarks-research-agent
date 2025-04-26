"""
Helper functions for the NYC Landmarks Research Agent.
Provides utility functions used across the application.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def safe_get(obj: Optional[Dict[str, Any]], path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary using dot notation.

    Args:
        obj: Dictionary to get value from
        path: Path to value using dot notation (e.g., "metadata.title")
        default: Default value to return if path not found

    Returns:
        Value at path or default if not found
    """
    if obj is None:
        return default

    parts = path.split(".")

    current: Any = obj
    try:
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return default

            if current is None:
                return default

        return current
    except Exception:
        return default


def clean_text(text: Optional[str]) -> str:
    """
    Clean text by removing extra whitespace and normalizing line breaks.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple whitespace with a single space
    text = re.sub(r"\s+", " ", text)

    # Replace multiple line breaks with at most two
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace
    return text.strip()


def truncate_text(text: Optional[str], max_length: int = 1000) -> Optional[str]:
    """
    Truncate text to a maximum length while preserving word boundaries.

    Args:
        text: Text to truncate
        max_length: Maximum length of truncated text

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    # Truncate at word boundary
    truncated = text[:max_length].rsplit(" ", 1)[0]

    # Add ellipsis
    return f"{truncated}..."


def format_date(date_str: Optional[str]) -> Optional[str]:
    """
    Format a date string into a more readable format.

    Args:
        date_str: Date string in ISO format (e.g., "2021-01-01T00:00:00")

    Returns:
        Formatted date string (e.g., "January 1, 2021")
    """
    if date_str is None:
        return None

    try:
        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str


def get_env_bool(name: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.

    Args:
        name: Name of environment variable
        default: Default value if variable not found or invalid

    Returns:
        Boolean value of environment variable
    """
    value = os.environ.get(name)
    if value is None:
        return default

    value = value.lower()
    if value in ("1", "true", "yes", "y", "on"):
        return True
    if value in ("0", "false", "no", "n", "off"):
        return False

    return default


def to_json(obj: Any) -> str:
    """
    Convert an object to a JSON string with proper formatting.

    Args:
        obj: Object to convert to JSON

    Returns:
        JSON string
    """
    return json.dumps(obj, default=str, indent=2)


def parse_landmark_id(text: str) -> Optional[str]:
    """
    Parse a landmark ID from text.

    Args:
        text: Text to parse landmark ID from

    Returns:
        Landmark ID if found, None otherwise
    """
    match = re.search(r"LP-\d{5}", text)
    return match.group(0) if match else None


def extract_digits(text: str) -> str:
    """
    Extract digits from text.

    Args:
        text: Text to extract digits from

    Returns:
        String containing only digits
    """
    return "".join(c for c in text if c.isdigit())


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Levenshtein distance between the strings
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match(query: str, choices: List[str], threshold: float = 0.3) -> Optional[str]:
    """
    Find the closest match for a query in a list of choices using fuzzy matching.

    Args:
        query: Query string to match
        choices: List of choices to match against
        threshold: Threshold for considering a match (0.0-1.0)

    Returns:
        Closest match if found, None otherwise
    """
    if not choices:
        return None

    if query is None:
        return None

    query = query.lower()
    best_match = None
    best_score = float("-inf")

    for choice in choices:
        choice_lower = choice.lower()

        # Exact match takes precedence
        if query == choice_lower:
            return choice

        # Check if query is contained in choice
        if query in choice_lower:
            score = len(query) / len(choice_lower)
            score = min(score + 0.2, 1.0)  # Boost containment matches
        else:
            # Calculate Levenshtein distance
            distance = levenshtein_distance(query, choice_lower)
            max_len = max(len(query), len(choice_lower))
            score = 1 - (distance / max_len)

        if score > best_score:
            best_score = score
            best_match = choice

    return best_match if best_score >= threshold else None
