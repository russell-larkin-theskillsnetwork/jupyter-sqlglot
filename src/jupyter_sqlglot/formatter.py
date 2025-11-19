"""SQL formatting logic using SQLGlot.

Handles the core formatting functionality including:
- F-string interpolation masking/unmasking
- SQLGlot integration for SQL formatting
- Error handling for malformed SQL
"""

import re
import logging
from typing import Tuple, Dict, Optional
import sqlglot
from sqlglot.errors import ParseError

from .magics import SQLGlotConfig

logger = logging.getLogger(__name__)


# Placeholder pattern for masked interpolations
MASK_PATTERN = "__MASK_{}_"


def mask_interpolations(sql: str) -> Tuple[str, Dict[str, str]]:
    """Mask Python f-string interpolations before SQL formatting.

    Replaces {expr} with __MASK_0__, __MASK_1__, etc. to prevent SQLGlot
    from trying to parse Python expressions as SQL.

    Args:
        sql: SQL string potentially containing f-string interpolations

    Returns:
        Tuple of (masked_sql, mapping) where mapping is {placeholder: original_expr}

    Example:
        >>> masked, mapping = mask_interpolations("SELECT * FROM {table}")
        >>> masked
        "SELECT * FROM __MASK_0__"
        >>> mapping
        {"__MASK_0__": "{table}"}
    """
    mapping = {}
    counter = 0

    # Pattern to match {expr} but not {{escaped}}
    # This matches single braces with content, avoiding escaped double braces
    pattern = r'\{([^{}]+)\}'

    def replace_func(match):
        nonlocal counter
        original = match.group(0)  # Full match including braces
        placeholder = MASK_PATTERN.format(counter)
        mapping[placeholder] = original
        counter += 1
        return placeholder

    masked_sql = re.sub(pattern, replace_func, sql)

    if mapping:
        logger.debug(f"Masked {len(mapping)} interpolations")

    return masked_sql, mapping


def unmask_interpolations(sql: str, mapping: Dict[str, str]) -> str:
    """Restore Python f-string interpolations after SQL formatting.

    Replaces __MASK_N__ placeholders with their original {expr} values.

    Args:
        sql: Formatted SQL with placeholders
        mapping: Dictionary mapping placeholders to original expressions

    Returns:
        SQL string with interpolations restored
    """
    result = sql
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)

    if mapping:
        logger.debug(f"Unmasked {len(mapping)} interpolations")

    return result


def format_sql(sql: str, config: SQLGlotConfig) -> Optional[str]:
    """Format SQL using SQLGlot.

    Args:
        sql: SQL string to format
        config: Configuration for formatting

    Returns:
        Formatted SQL string, or None if parsing fails
    """
    try:
        # Get SQLGlot parameters from config
        kwargs = config.to_sqlglot_kwargs()

        # Transpile the SQL (parse and format)
        formatted_list = sqlglot.transpile(sql, **kwargs)

        if not formatted_list:
            logger.warning("SQLGlot returned empty result")
            return None

        # Join multiple statements if present
        formatted = "\n\n".join(formatted_list)

        # Apply uppercase to keywords if configured
        if config.uppercase:
            # SQLGlot handles this internally, but we could post-process if needed
            pass

        return formatted

    except ParseError as e:
        logger.warning(f"SQLGlot parse error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during SQL formatting: {e}")
        return None


def format_sql_string(sql_content: str,
                     is_fstring: bool,
                     config: SQLGlotConfig) -> Optional[str]:
    """Format a SQL string, handling f-string interpolations if needed.

    This is the main entry point for formatting SQL strings. It coordinates
    the masking, formatting, and unmasking process.

    Args:
        sql_content: The SQL string content (without outer quotes)
        is_fstring: Whether this is an f-string (needs masking)
        config: Formatting configuration

    Returns:
        Formatted SQL string, or None if formatting failed

    Example:
        >>> config = SQLGlotConfig()
        >>> format_sql_string("select * from users", False, config)
        "SELECT\\n    *\\nFROM users"
    """
    # Step 1: Mask interpolations if this is an f-string
    if is_fstring:
        masked_sql, mapping = mask_interpolations(sql_content)
    else:
        masked_sql = sql_content
        mapping = {}

    # Step 2: Format with SQLGlot
    formatted_sql = format_sql(masked_sql, config)

    if formatted_sql is None:
        # Formatting failed, return None
        return None

    # Step 3: Unmask interpolations if needed
    if mapping:
        formatted_sql = unmask_interpolations(formatted_sql, mapping)

    return formatted_sql


def should_format(original: str, formatted: str) -> bool:
    """Determine if the formatted version is different enough to apply.

    Args:
        original: Original SQL string
        formatted: Formatted SQL string

    Returns:
        True if formatting should be applied (strings differ meaningfully)
    """
    # Normalize whitespace for comparison
    orig_normalized = " ".join(original.split())
    fmt_normalized = " ".join(formatted.split())

    # Only apply if they differ (ignoring pure whitespace changes is optional)
    return original != formatted
