"""
Unit tests for helper functions.
"""
import pytest
from src.util.helpers import (
    safe_get, clean_text, truncate_text,
    format_date, get_env_bool, to_json,
    parse_landmark_id, extract_digits,
    levenshtein_distance, fuzzy_match
)


class TestHelpers:
    """Tests for helper functions."""

    def test_safe_get(self):
        """Test safely getting nested values from a dictionary."""
        # Arrange
        test_dict = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }

        # Act & Assert
        assert safe_get(test_dict, "level1.level2.level3") == "value"
        assert safe_get(test_dict, "level1.level2.nonexistent") is None
        assert safe_get(test_dict, "nonexistent") is None
        assert safe_get(test_dict, "nonexistent", "default") == "default"
        assert safe_get(None, "anything") is None

    def test_clean_text(self):
        """Test cleaning text."""
        # Arrange
        messy_text = "  This   has \n\n\n extra   spaces \t and newlines \n\n  "

        # Act
        cleaned = clean_text(messy_text)

        # Assert
        assert cleaned == "This has extra spaces and newlines"
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_truncate_text(self):
        """Test truncating text."""
        # Arrange
        long_text = "This is a very long text that should be truncated"

        # Act & Assert
        assert truncate_text(long_text, 10) == "This is a..."
        assert truncate_text(long_text, 100) == long_text
        assert truncate_text("", 10) == ""
        assert truncate_text(None, 10) is None

    def test_format_date(self):
        """Test formatting dates."""
        # Act & Assert
        assert format_date("2021-01-01T00:00:00") == "January 01, 2021"
        assert format_date("2021-01-01T00:00:00Z") == "January 01, 2021"
        assert format_date("invalid") == "invalid"
        assert format_date(None) is None

    def test_get_env_bool(self):
        """Test getting boolean values from environment variables."""
        # Arrange
        env_vars = {
            "TRUE_VAR": "true",
            "FALSE_VAR": "false",
            "ONE_VAR": "1",
            "ZERO_VAR": "0",
            "INVALID_VAR": "invalid"
        }

        # Act & Assert
        with pytest.MonkeyPatch.context() as mp:
            for k, v in env_vars.items():
                mp.setenv(k, v)

            assert get_env_bool("TRUE_VAR") is True
            assert get_env_bool("FALSE_VAR") is False
            assert get_env_bool("ONE_VAR") is True
            assert get_env_bool("ZERO_VAR") is False
            assert get_env_bool("INVALID_VAR") is False
            assert get_env_bool("NONEXISTENT_VAR") is False
            assert get_env_bool("NONEXISTENT_VAR", True) is True

    def test_to_json(self):
        """Test converting objects to JSON."""
        # Arrange
        obj = {"name": "Test", "value": 123}

        # Act
        json_str = to_json(obj)

        # Assert
        assert isinstance(json_str, str)
        assert '"name": "Test"' in json_str
        assert '"value": 123' in json_str

    def test_parse_landmark_id(self):
        """Test parsing landmark IDs."""
        # Act & Assert
        assert parse_landmark_id(
            "The landmark LP-00123 is famous") == "LP-00123"
        assert parse_landmark_id("No landmark ID here") is None
        assert parse_landmark_id(
            "Multiple LP-00123 and LP-45678") == "LP-00123"

    def test_extract_digits(self):
        """Test extracting digits from text."""
        # Act & Assert
        assert extract_digits("abc123def456") == "123456"
        assert extract_digits("No digits") == ""
        assert extract_digits("") == ""

    def test_levenshtein_distance(self):
        """Test calculating Levenshtein distance."""
        # Act & Assert
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3
        assert levenshtein_distance("abc", "abc") == 0

    def test_fuzzy_match(self):
        """Test fuzzy matching."""
        # Arrange
        choices = ["Flatiron Building",
                   "Empire State Building", "Chrysler Building"]

        # Act & Assert
        assert fuzzy_match("flatiron", choices) == "Flatiron Building"
        assert fuzzy_match("empire", choices) == "Empire State Building"
        assert fuzzy_match(
            "chrsyelr", choices) == "Chrysler Building"  # Misspelled
        assert fuzzy_match("unknown", choices, threshold=0.7) is None
        assert fuzzy_match("query", []) is None
