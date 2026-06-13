import logging
import os

logger = logging.getLogger(__name__)


def first_csv(path):
    try:
        for entry in os.listdir(path):
            if entry.endswith(".csv"):
                return os.path.join(path, entry)
        return None
    except Exception as e:
        logger.info("Error %s has occurred", e)
        return None
