def normalize_search_term(value: str) -> str:
    """Trim + lowercase a free-text query before building a LIKE pattern."""
    return value.strip().lower()
