"""Jupyter notebook hooks for automatic SQL formatting.

This module handles the integration with Jupyter's execution pipeline:
- Registers pre_run_cell hooks to intercept cell execution
- Detects SQL content in cells
- Applies formatting
- Updates the frontend using shell.set_next_input()

IMPORTANT: Interoperability with jupyter-black
-------------------------------------------
This extension is designed to work alongside jupyter-black. Both extensions
hook into the pre_run_cell event, but they target different content:
- jupyter-black formats Python code
- jupyter-sqlglot formats SQL strings within Python code

To avoid conflicts:
1. We read the cell content from the event, which may already be modified by black
2. We only modify SQL strings, leaving Python code structure intact
3. We use shell.set_next_input() to update the frontend, same as jupyter-black
4. Load order recommendation: %load_ext jupyter_black, then %load_ext jupyter_sqlglot

This ensures that:
- Black formats Python first: x=[1,2,3] -> x = [1, 2, 3]
- SQLGlot then formats SQL strings within that formatted Python code
"""

import logging
from typing import Optional
from IPython.core.interactiveshell import InteractiveShell

from .magics import SQLGlotConfig, set_config
from .utils import find_sql_to_format
from .formatter import format_sql_string

logger = logging.getLogger(__name__)


# Global reference to the hook callback for unregistration
_registered_callback = None
# Global reference to the IPython shell for cell updates
_shell = None


def format_cell_content(cell_content: str, config: SQLGlotConfig) -> Optional[str]:
    """Format SQL content within a cell.

    Args:
        cell_content: The full cell content (possibly already modified by other formatters)
        config: Formatting configuration

    Returns:
        Modified cell content with formatted SQL, or None if no changes needed
    """
    # Find all SQL contexts in the cell (%%sql magics, spark.sql() calls, etc.)
    sql_contexts = find_sql_to_format(cell_content)

    if not sql_contexts:
        # No SQL found, no formatting needed
        logger.debug("No SQL contexts found in cell")
        return None

    logger.debug(f"Found {len(sql_contexts)} SQL context(s) to format")

    modified_content = cell_content
    changes_made = False

    # Process each SQL context
    # Work backwards through the string to maintain correct offsets
    for context in reversed(sql_contexts):
        sql_content = context['sql']
        is_fstring = context['is_fstring']
        start_pos = context['start']
        end_pos = context['end']

        # Format the SQL
        formatted_sql = format_sql_string(sql_content, is_fstring, config)

        if formatted_sql is None:
            # Formatting failed, skip this SQL
            logger.debug(f"Skipping SQL at position {start_pos} (parse failed)")
            continue

        if formatted_sql == sql_content:
            # No changes needed
            continue

        # Replace in the cell content
        # Need to reconstruct with appropriate quotes
        quote_style = context.get('quote_style', '"""')
        prefix = 'f' if is_fstring else ''

        # Preserve the structure - add newlines and basic indentation
        # Extract indentation from the original line where the quotes appear
        lines_before = modified_content[:start_pos].split('\n')
        last_line = lines_before[-1] if lines_before else ''
        base_indent = ' ' * (len(last_line) - len(last_line.lstrip()))

        # For triple-quoted strings, format with indentation
        if quote_style in ('"""', "'''"):
            # Add indentation to each line of formatted SQL
            sql_lines = formatted_sql.split('\n')
            indented_sql = '\n'.join(base_indent + '    ' + line if line.strip() else ''
                                      for line in sql_lines)
            formatted_string = f'{prefix}{quote_style}\n{indented_sql}\n{base_indent}{quote_style}'
        else:
            # Single line string
            formatted_string = f'{prefix}{quote_style}{formatted_sql}{quote_style}'

        modified_content = (
            modified_content[:start_pos] +
            formatted_string +
            modified_content[end_pos:]
        )
        changes_made = True

    if changes_made:
        logger.debug("SQL formatting applied")
        return modified_content

    return None


def pre_run_cell_hook(info):
    """Hook called before each cell execution.

    This is the main entry point for the formatting pipeline.

    Args:
        info: ExecutionInfo object from IPython containing cell details
    """
    try:
        # Get current configuration
        from .magics import get_config
        config = get_config()

        if config.debug:
            print("[jupyter-sqlglot] Hook fired")

        # Get cell content from the execution info
        # Note: This may already be modified by other formatters (e.g., jupyter-black)
        cell_content = info.raw_cell

        if not cell_content or not cell_content.strip():
            return

        # Format SQL within the cell
        if config.debug:
            print("[jupyter-sqlglot] Analyzing cell for SQL...")

        formatted_content = format_cell_content(cell_content, config)

        if formatted_content is None:
            # No changes needed
            if config.debug:
                print("[jupyter-sqlglot] No SQL formatting changes needed")
            return

        if config.debug:
            print("[jupyter-sqlglot] SQL formatted! Updating cell...")

        # Update the cell content in the execution pipeline
        # This makes the formatted code execute
        info.raw_cell = formatted_content

        # Update the frontend display using the same approach as jupyter-black
        # This shows the formatted code in the cell after execution
        if config.debug:
            print("[jupyter-sqlglot] Updating cell display...")

        if _shell:
            _shell.set_next_input(formatted_content, replace=True)
        else:
            logger.warning("Shell reference not available, cell display may not update")

        if config.debug:
            print("[jupyter-sqlglot] Done!")

    except Exception as e:
        # Never break cell execution due to formatting errors
        logger.error(f"Error in jupyter-sqlglot hook: {e}", exc_info=True)
        # Always print errors regardless of debug mode
        print(f"jupyter-sqlglot error: {e}")


def register_hooks(ipython: InteractiveShell, config: SQLGlotConfig):
    """Register the pre_run_cell hook with IPython.

    Args:
        ipython: The IPython instance
        config: Configuration to use for formatting
    """
    global _registered_callback, _shell

    # Store the shell reference for cell updates
    _shell = ipython

    # Set the global configuration
    set_config(config)

    # Register the hook
    ipython.events.register('pre_run_cell', pre_run_cell_hook)
    _registered_callback = pre_run_cell_hook

    logger.info("jupyter-sqlglot hooks registered")


def unregister_hooks(ipython: InteractiveShell):
    """Unregister the pre_run_cell hook from IPython.

    Args:
        ipython: The IPython instance
    """
    global _registered_callback, _shell

    if _registered_callback:
        try:
            ipython.events.unregister('pre_run_cell', _registered_callback)
            logger.info("jupyter-sqlglot hooks unregistered")
        except Exception as e:
            logger.error(f"Error unregistering hooks: {e}")
        finally:
            _registered_callback = None
            _shell = None
