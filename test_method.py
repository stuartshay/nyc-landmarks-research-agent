from typing import List


def _generate_suggested_queries(original_query: str, report_text: str) -> List[str]:
    """
    Generate suggested follow-up queries based on the original query and generated report.

    Args:
        original_query: The original research query
        report_text: The generated research report

    Returns:
        List of suggested follow-up queries
    """
    # This is a simplified implementation
    # In a real system, this would use NLP techniques or a separate LLM call

    # Placeholder implementation with common follow-up patterns
    suggestions = [
        "What is the architectural style of this landmark?",
        "When was this landmark designated?",
        "Who was the architect of this landmark?",
        "What are some similar landmarks in New York City?",
        "What is the historical significance of this landmark?",
    ]

    # Filter to just 3 suggestions
    return suggestions[:3]
