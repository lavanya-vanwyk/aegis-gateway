import logging
import sys
import json
from datetime import datetime, timezone


class JSONAuditFormatter(logging.Formatter):
    """
    Custom formatter to enforce structured JSON logs for audit trails.
    """

    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "event": record.getMessage(),
        }

        if hasattr(record, "audit_data"):
            log_record.update(record.audit_data)

        return json.dumps(log_record)


def setup_audit_logger():
    logger = logging.getLogger("aegis_audit")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONAuditFormatter())

    if not logger.handlers:
        logger.addHandler(handler)

    logger.propagate = False

    return logger


audit_logger = setup_audit_logger()
