import logging
import json
from datetime import datetime, timezone
from loguru import logger
import sys


def setup_audit_logger():
    logger.remove()

    logger.add(sys.stdout, format="{message}", level="INFO", serialize=True)
    logger.add(
        "audit_log",
        format="{message}",
        level="INFO",
        serialize=True,
        rotation="10 MB",
        retention="30 days",
    )
    return logger


audit_logger = setup_audit_logger()
