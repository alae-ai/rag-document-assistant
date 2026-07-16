"""
Application logging configuration.
"""

import logging
from pathlib import Path

from app.config import settings

# ---------------------------------------------------------------------
# Logs directory
# ---------------------------------------------------------------------

LOG_FILE = Path(settings.LOG_FILE)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Logger configuration
# ---------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name : str
        Usually __name__.

    Returns
    -------
    logging.Logger
    """
    return logging.getLogger(name)
