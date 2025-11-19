"""Configuration management for jupyter-sqlglot.

Handles extension configuration including SQL dialect, formatting options,
and integration settings.
"""

from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SQLGlotConfig:
    """Configuration settings for jupyter-sqlglot formatting.

    Attributes:
        dialect: SQL dialect for SQLGlot parsing/formatting (e.g., "spark")
        indent: Number of spaces for indentation
        uppercase: Whether to uppercase SQL keywords
        pretty: Whether to enable pretty printing with line breaks
        debug: Whether to print debug messages during formatting
    """
    dialect: str = "spark"
    indent: int = 4
    uppercase: bool = True
    pretty: bool = True
    debug: bool = False

    def to_sqlglot_kwargs(self) -> dict:
        """Convert configuration to SQLGlot transpile() keyword arguments.

        Returns:
            Dictionary of parameters suitable for sqlglot.transpile()
        """
        return {
            "read": self.dialect,
            "write": self.dialect,
            "pretty": self.pretty,
        }

    def validate(self):
        """Validate configuration parameters.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        if self.indent < 0:
            raise ValueError(f"indent must be non-negative, got {self.indent}")

        valid_dialects = ["spark", "spark2", "databricks"]
        if self.dialect not in valid_dialects:
            logger.warning(
                f"dialect '{self.dialect}' may not be fully supported. "
                f"Recommended: {valid_dialects}"
            )

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()


# Global configuration instance (set by hooks when extension loads)
_current_config: Optional[SQLGlotConfig] = None


def get_config() -> SQLGlotConfig:
    """Get the current active configuration.

    Returns:
        The current SQLGlotConfig instance, or default config if not set
    """
    global _current_config
    if _current_config is None:
        _current_config = SQLGlotConfig()
    return _current_config


def set_config(config: SQLGlotConfig):
    """Set the active configuration.

    Args:
        config: The SQLGlotConfig instance to use
    """
    global _current_config
    config.validate()
    _current_config = config
    logger.debug(f"Configuration updated: {config}")
