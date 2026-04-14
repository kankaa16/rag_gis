import re

MAX_QUERY_LENGTH = 300

BANNED_PATTERNS = [
    "ignore previous instructions",
    "system prompt",
    "delete database",
    "drop table",
]

def validate_query(query: str):

    if query is None:
        return False, "Query cannot be empty"

    query = query.strip()

    if len(query) == 0:
        return False, "Query cannot be empty"

    if len(query) > MAX_QUERY_LENGTH:
        return False, "Query too long"

    # Must contain letters
    if not re.search(r"[a-zA-Z]", query):
        return False, "Query must contain meaningful words"

    lower_query = query.lower()

    # Basic injection protection
    for pattern in BANNED_PATTERNS:
        if pattern in lower_query:
            return False, "Unsafe query detected"

    return True, None