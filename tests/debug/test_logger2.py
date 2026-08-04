"""
Test logger exception handling.
"""

from app.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    try:
        result = 10 / 0
        print(result)
    except Exception:
        logger.exception("An exception occurred during testing.")


if __name__ == "__main__":
    main()
