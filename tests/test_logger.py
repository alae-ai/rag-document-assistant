"""
Test the application logger.
"""

from app.utils.logger import get_logger


logger = get_logger(__name__)


def main():
    logger.debug("This is a DEBUG message.")
    logger.info("This is an INFO message.")
    logger.warning("This is a WARNING message.")
    logger.error("This is an ERROR message.")
    logger.critical("This is a CRITICAL message.")


if __name__ == "__main__":
    main()
