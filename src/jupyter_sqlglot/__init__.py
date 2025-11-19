"""jupyter-sqlglot: Jupyter extension for automatic Spark SQL formatting.

This extension automatically formats Spark SQL queries in Jupyter notebooks using SQLGlot.
It works similarly to jupyter-black but for SQL code within spark.sql() calls and %%sql magics.
"""

__version__ = "0.1.0"
__author__ = "Russell Larkin"

from typing import Optional
import logging

logger = logging.getLogger(__name__)


def load_ipython_extension(ipython):
    """Load the jupyter-sqlglot extension.

    Called by IPython when the extension is loaded via %load_ext jupyter_sqlglot.

    Args:
        ipython: The IPython instance
    """
    from .hooks import register_hooks
    from .magics import SQLGlotConfig

    # Initialize with default configuration
    config = SQLGlotConfig()

    # Register the pre_run_cell hook
    register_hooks(ipython, config)

    logger.info("jupyter-sqlglot extension loaded")
    print("jupyter-sqlglot loaded (SQLGlot-based Spark SQL formatter)")


def unload_ipython_extension(ipython):
    """Unload the jupyter-sqlglot extension.

    Called by IPython when the extension is unloaded.

    Args:
        ipython: The IPython instance
    """
    from .hooks import unregister_hooks

    unregister_hooks(ipython)

    logger.info("jupyter-sqlglot extension unloaded")


def init(
    dialect: str = "spark",
    indent: int = 4,
    uppercase: bool = True,
    pretty: bool = True,
    debug: bool = False,
):
    """Initialize jupyter-sqlglot with custom configuration.

    Alternative to %load_ext that allows passing configuration parameters.

    Args:
        dialect: SQL dialect for SQLGlot (default: "spark")
        indent: Number of spaces for indentation (default: 4)
        uppercase: Whether to uppercase SQL keywords (default: True)
        pretty: Whether to enable pretty printing (default: True)
        debug: Whether to print debug messages (default: False)

    Example:
        >>> import jupyter_sqlglot
        >>> jupyter_sqlglot.init(indent=2, uppercase=False)
        >>> jupyter_sqlglot.init(debug=True)  # Enable debug output
    """
    from IPython import get_ipython
    from .hooks import register_hooks
    from .magics import SQLGlotConfig

    ipython = get_ipython()
    if ipython is None:
        raise RuntimeError("jupyter-sqlglot must be run in an IPython environment")

    # Create configuration with custom parameters
    config = SQLGlotConfig(
        dialect=dialect, indent=indent, uppercase=uppercase, pretty=pretty, debug=debug
    )

    # Register hooks with custom config
    register_hooks(ipython, config)

    print(
        f"jupyter-sqlglot initialized (dialect={dialect}, indent={indent}, debug={debug})"
    )
