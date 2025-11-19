"""Utility functions for parsing and detecting SQL content in notebook cells.

This module provides regex patterns and helper functions to:
- Detect %%sql magic cells
- Find spark.sql() calls with various quote styles
- Identify f-strings vs regular strings
- Extract SQL content for formatting
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


# Regex pattern for %%sql magic at cell start
SQL_MAGIC_PATTERN = re.compile(
    r'^%%sql\s*\n(.+)',
    re.DOTALL | re.MULTILINE
)


# Regex pattern for spark.sql() calls
# Matches: spark.sql(f"...", f'...', f"""...""", "...", '...', """...""")
SPARK_SQL_PATTERN = re.compile(
    r'spark\.sql\s*\(\s*(f?)(\'\'\'|"""|\'|")(.+?)\2',
    re.DOTALL
)


# Pattern to detect f-string prefix
FSTRING_PREFIX_PATTERN = re.compile(r'^f["\']')


def is_sql_magic(cell_content: str) -> bool:
    """Check if a cell starts with %%sql magic.

    Args:
        cell_content: Full cell content

    Returns:
        True if cell starts with %%sql magic
    """
    return SQL_MAGIC_PATTERN.match(cell_content) is not None


def is_fstring(string_literal: str) -> bool:
    """Check if a string literal is an f-string.

    Args:
        string_literal: String literal including quotes (e.g., 'f"text"' or '"text"')

    Returns:
        True if the string is an f-string (starts with f' or f")
    """
    return string_literal.strip().startswith('f')


def extract_sql_from_magic(cell_content: str) -> Dict[str, Any]:
    """Extract SQL from a %%sql magic cell.

    Args:
        cell_content: Full cell content

    Returns:
        Dictionary with sql, start, end, is_fstring, and quote_style keys
        Returns None if no magic found
    """
    match = SQL_MAGIC_PATTERN.match(cell_content)
    if not match:
        return None

    sql_content = match.group(1)

    return {
        'sql': sql_content,
        'start': match.start(1),
        'end': match.end(1),
        'is_fstring': False,
        'quote_style': '',  # No quotes for magic cells
        'type': 'magic'
    }


def extract_spark_sql_calls(cell_content: str) -> List[Dict[str, Any]]:
    """Find all spark.sql() calls in the cell content.

    Args:
        cell_content: Full cell content

    Returns:
        List of dictionaries with sql, start, end, is_fstring, and quote_style keys
    """
    results = []

    for match in SPARK_SQL_PATTERN.finditer(cell_content):
        fstring_prefix = match.group(1)  # 'f' or ''
        quote_style = match.group(2)     # ', ", ''', or """
        sql_content = match.group(3)     # The SQL content

        # Determine if this is an f-string
        is_fstring_flag = bool(fstring_prefix)

        # Calculate positions for the string literal
        # We need to replace from the start of 'f' (or quotes if no f) to the end of closing quotes
        # Group 1: f prefix (may be empty)
        # Group 2: opening quotes
        # Group 3: SQL content
        # After group 3: closing quotes (same as group 2)

        # Start position: beginning of group 1 (f or where f would be)
        # If group 1 is empty, start at group 2
        if fstring_prefix:
            full_string_start = match.start(1)
        else:
            full_string_start = match.start(2)

        # End position: end of closing quotes
        # match.end() gives us the end of the entire regex match, which ends at closing quotes
        full_string_end = match.end()

        results.append({
            'sql': sql_content,
            'start': full_string_start,
            'end': full_string_end,
            'is_fstring': is_fstring_flag,
            'quote_style': quote_style,
            'type': 'spark_sql'
        })

    return results


def find_sql_to_format(cell_content: str) -> List[Dict[str, Any]]:
    """Find all SQL contexts in a cell that should be formatted.

    This is the main entry point for SQL detection. It finds:
    1. %%sql magic cells
    2. spark.sql() calls with various quote styles

    Args:
        cell_content: Full cell content

    Returns:
        List of SQL contexts, each a dict with:
        - sql: The SQL content to format
        - start: Start position in cell_content
        - end: End position in cell_content
        - is_fstring: Whether this is an f-string
        - quote_style: The quote style used
        - type: 'magic' or 'spark_sql'

    Note:
        Results are returned in order of appearance in the cell.
    """
    results = []

    # Check for %%sql magic first (takes precedence - entire cell is SQL)
    magic_result = extract_sql_from_magic(cell_content)
    if magic_result:
        results.append(magic_result)
        # If this is a magic cell, don't look for spark.sql() calls
        return results

    # Look for spark.sql() calls
    spark_sql_results = extract_spark_sql_calls(cell_content)
    results.extend(spark_sql_results)

    logger.debug(f"Found {len(results)} SQL context(s) to format")

    return results


def extract_interpolations(fstring_content: str) -> List[str]:
    """Extract Python interpolation expressions from an f-string.

    Args:
        fstring_content: Content of an f-string (without the f and quotes)

    Returns:
        List of interpolation expressions (without the braces)

    Example:
        >>> extract_interpolations("SELECT * FROM {table} WHERE id > {min_id}")
        ["table", "min_id"]
    """
    # Pattern to match {expr} but not {{escaped}}
    pattern = r'\{([^{}]+)\}'

    matches = re.findall(pattern, fstring_content)
    return matches
