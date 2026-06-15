import logging
import json
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_payload["exception_details"] = self.formatException(record.exc_info)
        return json.dumps(log_payload)

def configure_production_logging(component_name: str = "VAT-Validator") -> logging.Logger:
    logger = logging.getLogger(component_name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        console_stream = logging.StreamHandler(sys.stdout)
        console_stream.setFormatter(JSONFormatter())
        logger.addHandler(console_stream)
        
    return logger
